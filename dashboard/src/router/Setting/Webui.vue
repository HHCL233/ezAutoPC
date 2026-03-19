<script setup lang="ts"></script>
<template>
    <div class="home">
        <h2>WebUI设置</h2>
        <mdui-list>
            <mdui-list-item :headline="`选项${index}`" :description="`打开选项${index}后的操作`" v-for="index in 5"><mdui-switch
                    slot="end-icon"></mdui-switch></mdui-list-item>
        </mdui-list>
    </div>
</template>
<style scoped>
.home {
    margin: 24px;
}
</style>