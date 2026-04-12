<script setup lang="ts">
import { useConfigStore } from '@/stores/config';

const config = useConfigStore()
</script>
<template>
    <div class="about">
        <h1>ezAutoPC</h1>
        <span>版本 {{ config?.config?._version }}</span>
    </div>
</template>
<style scoped>
.about {
    position: fixed;
    left: 50%;
    transform: translate(-50%, 0);
    transform-origin: center;
    text-align: center;
}
</style>