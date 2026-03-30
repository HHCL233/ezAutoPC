import { ref } from 'vue'
import { generalWS } from '@/utils/fetch'
import { dialog } from 'mdui/functions/dialog'
import type { TextField } from 'mdui/components/text-field.js';
import type { ButtonIcon } from 'mdui/components/button-icon.js';
import type { Ref } from 'vue'

export function useChatSocket(sendButton: Ref<ButtonIcon | null>, inputField: Ref<TextField | null>) {
    const socket = generalWS('')
    const messagesList = ref<any>([])
    const currentMessage = ref('')
    const toolList = ref([])
    const allowTools = ref<any>([])

    socket.on('connect', () => {
        console.log('已成功连接到 WS 服务端');
        socket.emit('message', JSON.stringify({ 'type': 'getAllMessages' }));
        socket.emit('message', JSON.stringify({ 'type': 'getAllTools' }));
    });

    socket.on('response', (data) => {
        console.log('收到服务端消息:', data);
        if (data['type'] == "getAllMessages") {
            messagesList.value = data.msg;
            console.log("当前Token:" + data.token)
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
        } else if (data['type'] == "getAllTools") {
            const tools = JSON.parse(data['msg'])
            toolList.value = tools.allTools
            allowTools.value = tools.allowTools
        }
        scrollToBottom()
    });

    socket.on('disconnect', (reason) => {
        let code = 1006;
        if (reason === 'io server disconnect') code = 1000;
        againConnect(reason)
        console.log('连接已关闭:', code, reason);
    });

    socket.on('connect_error', function (error) {
        againConnect(error.message)
    });
    const sendMessage = (() => {
        if (inputField.value) {
            inputField.value.value = ''
        }
        scrollToBottom()
        socket.emit('message', JSON.stringify({ 'type': 'sendMessagesToAI', 'content': currentMessage.value }));
        socket.emit('message', JSON.stringify({ 'type': 'getAllMessages' }));
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

    const changeAllowTool = (toolName: string) => {
        if (allowTools.value.includes(toolName)) {
            allowTools.value = allowTools.value.filter((tool: string) => tool !== toolName)
            socket.emit('message', JSON.stringify({ 'type': 'notAllowedTool', 'msg': toolName }))
        } else {
            allowTools.value.push(toolName)
            socket.emit('message', JSON.stringify({ 'type': 'allowTool', 'msg': toolName }))
        }
    }

    return {
        socket,
        messagesList,
        currentMessage,
        sendMessage,
        toolList,
        allowTools,
        changeAllowTool
    }
}