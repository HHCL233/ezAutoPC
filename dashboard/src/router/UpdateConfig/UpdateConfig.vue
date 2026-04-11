<script setup lang="ts">
import { useConfigStore } from '@/stores/config';

const config = useConfigStore()
</script>
<template>
    <div class="update-config">
        <h1>更新配置</h1>
        <p>确定把配置迁移到家目录内吗?</p>
        <mdui-button>我们还没有准备好!</mdui-button>
    </div>
</template>
<style scoped>
.update-config {
    position: fixed;
    left: 16px;

}
</style>