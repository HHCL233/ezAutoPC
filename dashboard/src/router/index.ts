import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [{
    path: '/',
    name: 'Home',
    component: () => import('@/router/Home.vue'),
    meta: { title: '首页' }
  }],
})

export default router
