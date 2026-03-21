import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [{
    path: '/',
    name: 'Home',
    component: () => import('@/router/Home.vue'),
    meta: { title: '首页' }
  }, {
    path: '/setting',
    name: 'Setting',
    component: () => import('@/router/Setting/Setting.vue'),
    meta: { title: '设置' }
  }, {
    path: '/chat',
    name: 'Chay',
    component: () => import('@/router/Chat/Chat.vue'),
    meta: { title: '对话' }
  }],
})

export default router
