<script setup lang="ts">
import { marked } from 'marked';
import { useConfigStore } from '@/stores/config';
import { onMounted } from 'vue';

let config: any = useConfigStore()
const props = defineProps([
    'messages',
    'type'
])
console.log(config)
</script>
<template>
    <div class="chat-card" :class="type">
        <mdui-card class="chat-content">
            <!-- messages.content应该是不直接JSON.parse,这里改比较麻烦 -->
            <div v-if="(config.config?.autopc?.tool_call)">
                <div v-for="(value, index) in JSON.parse(messages.content)" class="message"
                    v-if="messages.role == 'system'">
                    <div class="message-content" v-if="value.type == 'message' || value.type == 'user'"
                        v-html="marked(value.arguments.content)">
                    </div>
                    <mdui-card variant="outlined" v-else-if="value.type == 'error'" class="message-nomessage-content">
                        遇到了错误: <br>
                        {{ value.arguments.content }}
                    </mdui-card>
                    <mdui-card variant="outlined" v-else-if="value.type != 'application'"
                        class="message-nomessage-content">
                        执行操作: <br>
                        {{ JSON.stringify(value) }}
                    </mdui-card>
                </div>
            </div>
            <div v-else>
                <div class="message-content" v-if="messages.role == 'user'">
                    {{ messages.content[0]['text'] }}
                </div>
                <mdui-card variant="outlined"
                    v-if="messages.role == 'assistant' && config.config?.autopc?.thinking == true && messages.name != 'system_notice'"
                    class="message-nomessage-content" clickable>
                    <mdui-collapse>
                        <mdui-collapse-item header="思考内容: "
                            v-html="marked(messages.reasoning_content ?? '')"></mdui-collapse-item>
                    </mdui-collapse>
                </mdui-card>
                <div class="message-content" v-if="messages.role == 'assistant'"
                    v-html="marked((messages.content) ?? '')">
                </div>
                <mdui-card variant="outlined" v-if="messages.role == 'assistant'"
                    v-for="(value, index) in messages.tool_calls" class="message-nomessage-content">
                    执行操作: <br>
                    {{ value.function.name }}
                    <br>参数: <br>
                    {{ value.function.arguments }}
                </mdui-card>
                <mdui-card variant="outlined" v-if="messages.role == 'tool'" class="message-nomessage-content">
                    已执行操作: <br>
                    {{ messages.name }}
                </mdui-card>
            </div>
        </mdui-card>
    </div>
</template>
<style scoped>
.chat-card {
    width: 100%;
}

.chat-card.user {
    width: 100%;
    text-align: right
}

.chat-card.application {
    display: none;
}


.chat-content {
    padding: 16px;
    margin: 12px;
    max-width: 80%;
}

.message-content {}

.message-nomessage-content {
    padding: 8px;
    margin-top: 4px;
    user-select: none;
}
</style>