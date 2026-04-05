<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useConfigStore } from '@/stores/config';

const config = useConfigStore()
const tips = config?.config?.tips
const randomTip = ref("")
onMounted(() => {
    randomTip.value = tips[(Math.floor(Math.random() * ((tips.length - 1) - 0 + 1)) + 0)]
})
</script>
<template>
    <div class="home">
        <h1>你好!</h1>
        <p>{{ randomTip }}</p>
    </div>
</template>
<style scoped>
.home {
    margin: 24px;
}
</style>