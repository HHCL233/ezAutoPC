<script setup lang="ts">
import { usePagesStore } from '@/stores/pages'
import ChatCard from '@/components/ChatCard.vue';
import { ApiFetch } from '@/utils/apiFetch'
import { onMounted, ref } from 'vue';
import { generalWS } from '@/utils/fetch';
import type { TextField } from 'mdui/components/text-field.js';
import type { ButtonIcon } from 'mdui/components/button-icon.js';
import { dialog } from 'mdui/functions/dialog.js';

const pages = usePagesStore()
const messagesList = ref<any>([])

const socket = generalWS("")
const currentMessage = ref('')

const inputField = ref<TextField | null>(null)
const sendButton = ref<ButtonIcon | null>(null)
const chatContainer = ref(null)

socket.on('connect', function () {
    console.log('已成功连接到 WS 服务端');
    socket.emit('message', JSON.stringify({ 'type': 'getAllMessages' }));
});

socket.on('response', function (data) {
    console.log('收到服务端消息：', data);
    if (data['type'] == "getAllMessages") {
        console.log('11', data.msg)
        messagesList.value = JSON.parse(JSON.stringify(data.msg));
        console.log('22', messagesList.value)
        scrollToBottom()
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
    againConnect(reason)
    console.log('连接已关闭:', code, reason);
});

socket.on('connect_error', function (error) {
    againConnect(error.message)
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
    scrollToBottom()
    socket.emit('message', JSON.stringify({ 'type': 'sendMessagesToAI', 'content': currentMessage.value }));
    socket.emit('message', JSON.stringify({ 'type': 'getAllMessages' }));
})

const updataCurrentMessage = ((message: any) => {
    currentMessage.value = message.target.value
    console.log(message.target.value)
})

const scrollToBottom = () => {
    window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth'
    });
};

const againConnect = (errorMessage: string) => {
    dialog({
        headline: "后端连接失败",
        description: `是否重新连接?`,
        actions: [
            {
                text: "否",
            },
            {
                text: "是",
                onClick: () => {
                    socket.connect()
                },
            }
        ]
    });
}
</script>
<template>
    <div class="chat" ref="chatContainer">
        <ChatCard v-for="(message, index) in messagesList" :key="index" :messages="message" :type="message.role" />
        <div class="message-space"></div>
        <div class="controls">
            <mdui-card variant="filled" class="input">
                <mdui-text-field class="input-field" label="问问 ezAutoAI" ref="inputField" @input="updataCurrentMessage"
                    @keydown.enter="sendMessage"></mdui-text-field>
                <mdui-button-icon icon="send" class="input-send" @click="sendMessage()"
                    ref="sendButton"></mdui-button-icon>
            </mdui-card>
            <p class="chat-tip">ezAutoPC 是一款 AI 工具，其操作未必正确无误</p>
        </div>
    </div>
</template>
<style scoped>
.chat {
    height: 100%;
    width: 100%;
    max-width: 720px;
    min-width: 75%;
    margin: 0 auto;
}

.controls {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 280px;
    pointer-events: none;
}

@media (prefers-color-scheme: light) {
    .controls {
        background: linear-gradient(to bottom, rgb(255, 255, 255, 0), rgb(200, 200, 200));
    }
}

@media (prefers-color-scheme: dark) {
    .controls {
        background: linear-gradient(to bottom, rgb(255, 255, 255, 0), rgb(18, 18, 18));
    }
}

.input {
    position: fixed;
    bottom: 48px;
    width: 60%;
    max-width: 720px;
    min-width: 320px;
    display: flex;
    height: 58px;
    margin: auto;
    left: 50%;
    transform: translate(-50%, 0);
    transform-origin: center;
    overflow: hidden;
    pointer-events: all;
}

.input-field {
    width: 100%;
    transform: translateY(2px);
}

.input-send {
    position: absolute;
    right: 8px;
    bottom: 50%;
    transform: translate(0, 50%);
    transform-origin: center;
}

.chat-tip {
    bottom: 0;
    position: fixed;
    left: 50%;
    transform: translate(-50%, 0);
    white-space: nowrap;
    text-align: center;
}

.message-space {
    height: 300px;
    width: 100%;
}
</style>