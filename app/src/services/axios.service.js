import axios from 'axios';
import store from '../store';
import router from '../router';

const api = axios.create({
  baseURL: '/api',
  validateStatus: (status) => status >= 200 && status < 400,
});

api.interceptors.request.use((config) => {
  const token = config.url === '/auth/refresh'
    ? store.getters.refreshToken
    : store.getters.accessToken;
  if (!token) return config;
  return {
    ...config,
    headers: {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    },
  };
});

let isRetry = false;

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const { response, config } = err;
    if (response?.status === 401 && !isRetry) {
      isRetry = true;
      try {
        const newToken = await store.dispatch('refresh');
        if (!newToken) router.push('/auth');
        return api({
          ...config,
          headers: {
            ...config.headers,
            Authorization: `Bearer ${newToken}`,
          },
        });
      } catch (refreshError) {
        if (refreshError.response?.data?.msg === 'Token expired') {
          router.push('/auth');
        }
      } finally {
        isRetry = false;
      }
    }
    return Promise.reject(err);
  },
);

export default api;
