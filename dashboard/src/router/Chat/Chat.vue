<script setup lang="ts">
import { usePagesStore } from '@/stores/pages'
import ChatCard from '@/components/ChatCard.vue';
import { ApiFetch } from '@/utils/apiFetch'
import { onMounted, ref } from 'vue';
import { generalWS } from '@/utils/fetch';
import type { TextField } from 'mdui/components/text-field.js';
import type { ButtonIcon } from 'mdui/components/button-icon.js';

const pages = usePagesStore()
const messagesList = ref<any>([])

const socket = generalWS("")
const currentMessage = ref('')

const inputField = ref<TextField | null>(null)
const sendButton = ref<ButtonIcon | null>(null)

socket.on('connect', function () {
    console.log('已成功连接到 WS 服务端');
    socket.emit('message', JSON.stringify({ 'type': 'getAllMessages' }));
});

socket.on('response', function (data) {
    console.log('收到服务端消息：', data);
    if (data['type'] == "getAllMessages") {
        const noSystemData = Array.isArray(data.msg) ? [...data.msg] : [];
        Object.entries(noSystemData).forEach(([indexStr, value]) => {
            const index = Number(indexStr);
            if (value && value.role === 'system') {
                noSystemData.splice(index, 1);
            } else if (value && value.role === 'user' && typeof value === 'object') {
                value.content = value.content[0]['text']
            }
        });
        messagesList.value = JSON.parse(JSON.stringify(noSystemData));
    } else if (data['type'] == "disabledSend") {
        if (sendButton.value && inputField.value) {
            sendButton.value.disabled = true;
            inputField.value.disabled = true;
        }
    } else if (data['type'] == "enableSend") {
        if (sendButton.value && inputField.value) {
            sendButton.value.disabled = false;
            inputField.value.disabled = false;
        }
    }
});

socket.on('disconnect', function (reason) {
    let code = 1006;
    if (reason === 'io server disconnect') code = 1000;
    console.log('连接已关闭:', code, reason);
});
/**
setInterval(() => {
    socket.emit('message', JSON.stringify({ 'type': 'getAllMessages' }));
}, 500)
**/
const sendMessage = (() => {
    if (inputField.value) {
        inputField.value.value = ''
    }
    socket.emit('message', JSON.stringify({ 'type': 'sendMessagesToAI', 'content': currentMessage.value }));
    socket.emit('message', JSON.stringify({ 'type': 'getAllMessages' }));
})

const updataCurrentMessage = ((message: any) => {
    currentMessage.value = message.target.value
    console.log(message.target.value)
})
</script>
<template>
    <div class="chat">
        <ChatCard v-for="(message, index) in messagesList" :messages="JSON.parse(message.content)"
            :type="[message.role == 'assistant' ? 'ai' : 'user']" />
        <div class="message-space"></div>
        <mdui-card variant="filled" class="input">
            <mdui-text-field rows="3" class="input-field" label="问问 ezAutoAI" ref="inputField"
                @change="updataCurrentMessage"></mdui-text-field>
            <mdui-button-icon icon="send" class="input-send" @click="sendMessage()" ref="sendButton"></mdui-button-icon>
        </mdui-card>
        <p class="chat-tip">ezAutoPC 是一款 AI 工具，其操作未必正确无误。</p>
    </div>
</template>
<style scoped>
.chat {
    height: 100%;
    width: 840px;
    margin: auto;
}

.input {
    position: fixed;
    bottom: 48px;
    width: 720px;
    display: flex;
    height: 115px;
    margin: auto;
    left: 50%;
    transform: translate(-50%, 0);
    transform-origin: center;
    overflow: hidden;
}

.input-field {
    width: 100%;
    transform: translateY(2px);
}

.input-send {
    position: absolute;
    right: 8px;
    bottom: 8px;
}

.chat-tip {
    bottom: 0;
    position: fixed;
    left: 50%;
    transform: translate(-50%, 0);
}

.message-space {
    height: 300px;
    width: 100%;
}
</style>