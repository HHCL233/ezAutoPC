<script setup lang="ts">
import './assets/fonts/fonts.css'
import { ref, onMounted, defineAsyncComponent } from 'vue'
import type { NavigationDrawer } from 'mdui';
import { usePagesStore } from '@/stores/pages'

const pages = usePagesStore()
const itemsDrawer = ref<NavigationDrawer | null>(null)

const openItemsDrawer = (() => {
  itemsDrawer.value!.open = true;
})

</script>

<template>
  <mdui-top-app-bar>
    <mdui-button-icon icon="menu" @click="openItemsDrawer()"></mdui-button-icon>
    <mdui-top-app-bar-title>ezAutoPC</mdui-top-app-bar-title>
    <mdui-button-icon icon="more_vert"></mdui-button-icon>
  </mdui-top-app-bar>
  <mdui-navigation-drawer close-on-overlay-click class="items-drawer" modal ref="itemsDrawer">
    <mdui-list>
      <mdui-list-item rounded v-for="(value, key, index) in pages.pageList">{{ value.title }}</mdui-list-item>
    </mdui-list>
  </mdui-navigation-drawer>
  <mdui-tabs value="tab-0" class="children-tabs" full-width v-if="JSON.stringify(pages.page.children) != '[]'">
    <mdui-tab v-for="(value, index) in pages.page.children" :value="`tab-${index}`">{{ value.title }}</mdui-tab>

    <mdui-tab-panel slot="panel" v-for="(value, index) in pages.page.children" :value="`tab-${index}`">
      <component :is="value.component" :key="index"></component>
    </mdui-tab-panel>
  </mdui-tabs>
  <RouterView v-else />
</template>

<style scoped></style>
<style>
body,
html {
  margin: 0;
}


* {
  font-family: OPPOSans;
}
</style>