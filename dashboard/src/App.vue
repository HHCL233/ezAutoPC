<script setup lang="ts">
import './assets/fonts/fonts.css'
import { ref, onMounted, defineAsyncComponent } from 'vue'
import type { NavigationDrawer } from 'mdui';
import { usePagesStore, type PageKey } from '@/stores/pages'

const pages = usePagesStore()
const itemsDrawer = ref<NavigationDrawer | null>(null)

const openItemsDrawer = (() => {
  itemsDrawer.value!.open = true;
})

const pushPage = ((name: PageKey) => {
  itemsDrawer.value!.open = false;
  pages.pushPage(name)
})
</script>

<template>
  <mdui-top-app-bar scroll-behavior="elevate">
    <mdui-button-icon icon="menu" @click="openItemsDrawer()"></mdui-button-icon>
    <mdui-top-app-bar-title>ezAutoPC</mdui-top-app-bar-title>
    <mdui-button-icon icon="more_vert"></mdui-button-icon>
  </mdui-top-app-bar>
  <mdui-navigation-drawer close-on-overlay-click class="items-drawer" modal ref="itemsDrawer">
    <mdui-list>
      <mdui-list-item rounded v-for="(value, key, index) in pages.pageList" @click="pushPage(key)">{{ value.title
        }}</mdui-list-item>
    </mdui-list>
  </mdui-navigation-drawer>
  <RouterView />
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

::-webkit-scrollbar {
  width: 4px;
  position: absolute;
  right: 0;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #88888880;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>