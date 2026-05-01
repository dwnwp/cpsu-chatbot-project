import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/useAuthStore';
import LoginView from '../views/LoginView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import KnowledgeView from '../views/KnowledgeView.vue'
import ImageView from '../views/ImageView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Login',
      component: LoginView,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: NotFoundView,
    },
    {
      path: '/knowledge',
      name: 'Knowledge',
      component: KnowledgeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/images',
      name: 'Images',
      component: ImageView,
      meta: { requiresAuth: true }
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  if (to.name === 'NotFound') {
    return next();
  }

  const authStore = useAuthStore();

  if (authStore.isLoading) {
    await authStore.verifySession();
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
  } 

  else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Knowledge' });
  } 

  else {
    next();
  }
});

export default router
