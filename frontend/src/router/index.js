import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../pages/HomePage.vue'),
  },
  {
    path: '/room/:roomId',
    name: 'room',
    component: () => import('../pages/RoomPage.vue'),
    meta: { requiresNickname: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresNickname) {
    const user = useUserStore()
    if (!user.nickname) {
      return { name: 'home', query: { redirect: to.fullPath } }
    }
  }
})

export default router
