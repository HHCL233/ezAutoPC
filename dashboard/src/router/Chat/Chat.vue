<script setup lang="ts">
import { usePagesStore } from '@/stores/pages'
import ChatCard from '@/components/ChatCard.vue';
import { ApiFetch } from '@/utils/apiFetch'
import { onMounted, ref } from 'vue';
import { generalWS } from '@/utils/fetch';
import type { TextField } from 'mdui/components/text-field.js';
import type { ButtonIcon } from 'mdui/components/button-icon.js';
import { dialog } from 'mdui/functions/dialog.js';
import { useChatSocket } from '@/composables/useChatSocket';
import { values } from 'lodash';

const inputField = ref<TextField | null>(null)
const sendButton = ref<ButtonIcon | null>(null)
const chatContainer = ref(null)
const { messagesList, currentMessage, sendMessage, toolList, allowTools, changeAllowTool } = useChatSocket(sendButton, inputField)

const updataCurrentMessage = ((message: any) => {
    currentMessage.value = message.target.value
})

const scrollToBottom = () => {
    window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth'
    });
};

onMounted(() => {
    scrollToBottom()
})
</script>
<template>
    <div class="chat" ref="chatContainer">
        <ChatCard v-for="(message, index) in messagesList" :key="index" :messages="message" :type="message.role" />
        <div class="message-space"></div>
        <div class="controls">
            <mdui-card variant="filled" clickable class="tools-setting">
                <mdui-collapse>
                    <mdui-collapse-item :header="`本会话工具权限 (${allowTools.length}/${toolList.length})`">
                        <div class="tools-setting-checkbox-list">
                            <mdui-checkbox v-for="value in toolList" :checked="allowTools.includes(value)"
                                @change="changeAllowTool(value)">{{ value
                                }}</mdui-checkbox>
                        </div>
                    </mdui-collapse-item>
                </mdui-collapse>
            </mdui-card>
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
    display: flex;
    flex-direction: column;
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

.tools-setting {
    position: fixed;
    bottom: 120px;
    left: 50%;
    transform: translate(-50%, 0);
    width: 50%;
    max-width: 640px;
    min-width: 320px;
    height: auto;
    pointer-events: all;
    padding: 8px;
}

.tools-setting-checkbox-list {
    margin-top: 4px;
    display: flex;
    flex-direction: column;
    flex-wrap: wrap;
}

.tools-setting-open {
    right: 8px;
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