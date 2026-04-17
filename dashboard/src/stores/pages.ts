import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import SettingWebui from '@/router/Setting/Webui.vue'
import SettingAutoPC from '@/router/Setting/AutoPC.vue'

interface PageChild {
  path: string
  title: string,
  component: RouteRecordRaw['component']
}
interface PageItem {
  path: string
  title: string
  children: PageChild[]
}
export type PageKey = 'home' | 'chat' | 'setting' | 'about' | 'login'
export const usePagesStore = defineStore('pages', () => {
  const router = useRouter()
  const route = useRoute()
  const pageList = ref<Record<PageKey, PageItem>>({
    home: {
      path: '',
      title: '首页',
      children: []
    },
    chat: {
      path: 'chat',
      title: '聊天',
      children: []
    },
    setting: {
      path: 'setting',
      title: '设置',
      children: [{
        path: 'webui-setting',
        title: 'WebUI设置',
        component: SettingWebui,
      },
      {
        path: 'ezautopc-setting',
        title: '本体设置',
        component: SettingAutoPC,
      },]
    }, about: {
      path: 'about',
      title: '关于',
      children: []
    }, login: {
      path: 'login',
      title: '登录',
      children: []
    },
  })
  const page = ref<PageItem>(pageList.value.home)
  function pushPage(name: PageKey) {
    const targetPage = pageList.value[name]
    page.value = targetPage
    router.push(`/${targetPage.path}`)
  }
  return { page, pushPage, pageList }
})
