import { createStore } from 'vuex';
import router from '../router';
import Auth from '../services/auth.service';

function isExpired(token) {
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch (err) {
    return true;
  }
}

export default createStore({
  state: {
    accessToken: localStorage.getItem('__accsToken') || null,
    refreshToken: localStorage.getItem('__rfshToken') || null,
    isAuth: !isExpired(localStorage.getItem('__accsToken')),
    user: localStorage.getItem('__usr') || null,
    expiresAt: localStorage.getItem('__expires') || null,
    loading: false,
  },
  getters: {
    isAuth: (state) => state.isAuth,
    accessToken: (state) => state.accessToken,
    refreshToken: (state) => state.refreshToken,
    expiresAt: (state) => state.expiresAt,
    user: (state) => state.user,
    loading: (state) => state.loading,
  },
  mutations: {
    setTokens(state, accs, rfsh = null, expiresAt = null) {
      state.accessToken = accs;
      state.refreshToken = rfsh;
      state.isAuth = true;
      localStorage.setItem('__accsToken', accs);
      if (rfsh) localStorage.setItem('__rfshToken', rfsh);
      if (expiresAt) localStorage.setItem('__expires', expiresAt);
    },
    clearSession(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuth = false;
      localStorage.removeItem('__accsToken');
      localStorage.removeItem('__rfshToken');
    },
    setUser(state, user) {
      state.user = user;
      localStorage.setItem('__usr', JSON.stringify(user));
    },
    setLoading(state, value) {
      state.loading = value;
    },
  },
  actions: {
    async login({ commit }, creds) {
      return Auth.login(creds)
        .then(({ body, status }) => {
          commit('setTokens', body.access_token, body.refresh_token, body.expires_at);
          commit('setUser', { email: body.email, uid: body.uid });
          return status;
        })
        .catch((err) => err);
    },
    async register(_, payload) {
      await Auth.register(payload);
    },
    async refresh({ state, commit }) {
      return Auth.refresh(state.refreshToken)
        .then((body) => {
          commit('setTokens', body);
          state.isAuth = true;
          return body.token;
        });
    },
    async logout({ commit }) {
      commit('clearSession');
      router.push('/');
    },
  },
});
