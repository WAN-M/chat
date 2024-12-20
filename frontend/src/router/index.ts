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
      component: ChatView,
      meta: { requiresAuth: true }
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

router.beforeEach((to, from, next) => {
  const isLoggedIn = sessionStorage.getItem('user');
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 如果路由需要登录
    if (!isLoggedIn) {
      next({ path: '/login' }); // 未登录，重定向到登录页面
    } else {
      next(); // 已登录，允许访问
    }
  } else {
    next(); // 不需要登录，直接放行
  }
});

export default router
