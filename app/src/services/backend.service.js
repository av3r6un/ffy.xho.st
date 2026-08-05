import api from './axios.service';

class Backend {
  msg = null;

  status = 'error';

  manageResp({ data }) {
    let body = null;
    if (data?.status === 'success') {
      body = data.body;
    }
    this.msg = body?.message ?? null;
    this.status = body?.status ?? 'error';
    return body;
  }

  manageError(err) {
    const status = err?.response?.status;
    const envelope = err?.response?.data?.data;
    this.msg = envelope?.message ?? err?.message ?? 'Request failed';
    if (status >= 400 && status <= 500) {
      this.msg = status === 500 ? 'Server error' : this.msg;
      return Promise.reject(err);
    }
    return Promise.resolve(err);
  }

  async get(url, params) {
    return api
      .get(url, { params })
      .then((resp) => this.manageResp(resp))
      .catch((err) => this.manageError(err));
  }

  async post(url, data) {
    return api
      .post(url, data)
      .then((resp) => this.manageResp(resp))
      .catch((err) => this.manageError(err));
  }
}

export default Backend;
