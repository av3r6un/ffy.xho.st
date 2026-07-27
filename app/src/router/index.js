import { createRouter, createWebHashHistory } from 'vue-router';
import Index from '../views/Index.vue';
import Watch from '../views/Watch.vue';

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
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
