<script setup lang="ts">
import { usePagesStore } from '@/stores/pages'

const pages = usePagesStore()
</script>
<template>
    <div class="setting">
        <mdui-tabs value="tab-0" class="children-tabs" full-width>
            <mdui-tab v-for="(value, index) in pages.pageList.setting.children" :value="`tab-${index}`">{{ value.title
                }}</mdui-tab>
            <mdui-tab-panel slot="panel" v-for="(value, index) in pages.pageList.setting.children"
                :value="`tab-${index}`" class="component">
                <component :is="value.component" :key="index"></component>
            </mdui-tab-panel>
        </mdui-tabs>
    </div>
</template>
<style scoped></style>