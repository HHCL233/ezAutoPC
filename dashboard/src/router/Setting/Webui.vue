<script setup lang="ts"></script>
<template>
    <div class="setting-webui">
        <h2 class="setting-title">WebUI设置</h2>
        <mdui-list class="setting-webui-list">
            <mdui-list-item :headline="`选项${index}`" :description="`打开选项${index}后的操作`" v-for="index in 0"><mdui-checkbox
                    slot="end-icon"></mdui-checkbox></mdui-list-item>
        </mdui-list>
        <mdui-fab icon="save" class="setting-webui-save" @click=""></mdui-fab>
    </div>
</template>
<style scoped>
.setting-title {
    font-weight: normal;
}

.setting-webui-list {
    margin: -8px -16px;
}

.setting-webui {
    margin: 16px;
}

.setting-webui-save {
    position: fixed;
    right: 36px;
    bottom: 36px;
}
</style>