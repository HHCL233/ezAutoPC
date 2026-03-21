<script setup lang="ts"></script>
<template>
    <div class="setting-webui">
        <h2>WebUI设置</h2>
        <mdui-list class="setting-webui-list">
            <mdui-list-item :headline="`选项${index}`" :description="`打开选项${index}后的操作`"
                v-for="index in 100"><mdui-checkbox slot="end-icon"></mdui-checkbox></mdui-list-item>
        </mdui-list>
    </div>
</template>
<style scoped>
.setting-webui-list {
    margin: -8px -16px;
}

.setting-webui {
    margin: 16px;
}
</style>