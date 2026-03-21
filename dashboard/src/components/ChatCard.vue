<script setup lang="ts">
import { List } from 'mdui';

const props = defineProps([
    'messages',
    'type'
])
</script>
<template>
    <div class="chat-card" :class="type">
        <mdui-card class="chat-content">
            <div v-for="(value, index) in messages" class="message">
                <div class="message-content" v-if="value.type == 'message' || value.type == 'user'">
                    {{ value.arguments.content }}
                </div>
                <mdui-card variant="outlined" v-else-if="value.type == 'error'" class="message-nomessage-content">
                    遇到了错误: <br>
                    {{ value.arguments.content }}
                </mdui-card>
                <mdui-card variant="outlined" v-else-if="value.type != 'application'" class="message-nomessage-content">
                    执行操作: <br>
                    {{ JSON.stringify(value) }}
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