import { createRouter, createWebHashHistory } from 'vue-router';
import store from '../store';
import Index from '../views/Index.vue';
import Watch from '../views/Watch.vue';
import Auth from '../views/Auth.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: Index,
  },
  {
    path: '/watch',
    name: 'watch',
    component: Watch,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/login',
    name: 'auth',
    component: Auth,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  if (to.path !== '/login' && !store.getters.isAuth) {
    if ((store.getters.refreshExpired * 1000) > Date.now()) {
      const newToken = await store.dispatch('refresh');
      next(newToken ? to.path : '/login');
    } else {
      next('/login', { query: { from: from.path } });
    }
  } else if (to.path === '/login' && store.getters.isAuth) {
    next('/');
  } else {
    next();
  }
});

export default router;
