import axios from 'axios';

const api = axios.create({
  baseURL: '/auth',
});

class Auth {
  static login(creds) {
    return api
      .post('/', creds)
      .then((resp) => resp.data);
  }

  static register(payload) {
    return api.post('/register', payload).then((resp) => resp.data);
  }

  static refresh(rfshToken) {
    return api
      .post('/refresh', {}, { headers: { Authorization: `Bearer ${rfshToken}` } })
      .then((resp) => resp.data);
  }
}

export default Auth;
