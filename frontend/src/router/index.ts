import { createRouter, createWebHashHistory } from 'vue-router'
import RegisterView from '@/views/login/register-view.vue'
import LoginView from '@/views/login/login-view.vue'
import ChatView from '@/views/chat/chat-view.vue'
// import AnalyzeResultView from '@/views/code/analyze/analyze-result-view.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/chat',
      component: ChatView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
  ]
})

export default router
