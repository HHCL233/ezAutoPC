<script setup lang="ts">
import { marked } from 'marked';
import { useConfigStore } from '@/stores/config';
import { onMounted, ref } from 'vue';

const config: any = useConfigStore()
const props = defineProps([
    'messages',
    'type'
])
const currentConfig = ref<any>()
onMounted(async () => {
    await config.getConfig()
    if (config.config.autopc.config_index >= config.config.autopc.config_list.length) {
        config.config.autopc.config_index = config.config.autopc.config_list.length - 1
    }
    currentConfig.value = config.config.autopc.config_list[config.config.autopc.config_index]
})
</script>
<template>
    <div class="chat-card" :class="type">
        <mdui-card class="chat-content">
            <div>
                <div class="message-content" v-if="messages.role == 'user'">
                    {{ messages.content[0]['text'] }}
                </div>
                <mdui-card variant="outlined" v-if="messages.role == 'assistant' && currentConfig?.thinking == true"
                    class="message-nomessage-content" clickable>
                    <mdui-collapse>
                        <mdui-collapse-item header="思考内容: " v-html="marked(messages.reasoning_content ?? '')"
                            v-if="messages.name != 'system_notice'"></mdui-collapse-item>
                        <mdui-collapse-item header="详细信息: " v-html="marked(messages.reasoning_content ?? '')"
                            v-else-if="messages.name == 'system_notice'"></mdui-collapse-item>
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