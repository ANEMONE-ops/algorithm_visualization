/**
 * 算法可视化系统 - API通信层
 */

const API_BASE = 'http://localhost:8001';

const API = {
    _token: null,
    _tokenLoaded: false,

    _loadToken() {
        if (!this._tokenLoaded) {
            this._token = localStorage.getItem('algo_viz_token') || '';
            this._tokenLoaded = true;
        }
        return this._token;
    },

    setToken(token) {
        this._token = token || '';
        this._tokenLoaded = true;
        if (token) {
            localStorage.setItem('algo_viz_token', token);
        } else {
            localStorage.removeItem('algo_viz_token');
        }
    },

    getToken() {
        return this._loadToken();
    },

    async request(method, path, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const opts = { method, headers };
        if (body && method !== 'GET') {
            opts.body = JSON.stringify(body);
        }

        const url = `${API_BASE}${path}`;
        let resp;
        try {
            resp = await fetch(url, opts);
        } catch (e) {
            throw new Error('网络连接失败，请确认后端服务已启动');
        }

        if (resp.status === 401) {
            this.setToken('');
            window.location.href = '/login.html';
            throw new Error('登录已过期，请重新登录');
        }

        const data = await resp.json().catch(() => ({}));

        if (!resp.ok) {
            throw new Error(data.detail || data.error || `请求失败(${resp.status})`);
        }

        return data;
    },

    get(path) { return this.request('GET', path); },
    post(path, body) { return this.request('POST', path, body); },
    delete(path) { return this.request('DELETE', path); },

    // === 认证 ===
    login(username, password) { return this.post('/api/auth/login', { username, password }); },
    register(username, password) { return this.post('/api/auth/register', { username, password }); },
    getMe() { return this.get('/api/auth/me'); },

    // === 算法 ===
    getAlgorithms() { return this.get('/api/algorithms'); },
    getAlgorithm(id) { return this.get(`/api/algorithms/${id}`); },
    runAlgorithm(algoId, data) { return this.post('/api/algorithms/run', { algorithm_id: algoId, data }); },
    getRandomData(algoId) { return this.post(`/api/algorithms/random-data?algorithm_id=${algoId}`); },
    validateInput(algoId, data) { return this.post(`/api/algorithms/validate?algorithm_id=${algoId}`, data); },
    getTestCases(algoId) { return this.get(`/api/algorithms/${algoId}/test-cases`); },

    // === AI对话 ===
    chat(message, algoContext, history) {
        return this.post('/api/ai/chat', { message, algorithm_context: algoContext, conversation_history: history });
    },

    // === 对比 ===
    getComparePairs() { return this.get('/api/compare/pairs'); },
    runCompare(pairId, data) { return this.post('/api/compare/run', { pair_id: pairId, data }); },

    // === 导出 ===
    saveLog(data) { return this.post('/api/export/save-log', data); },
    getLogs(algoType, limit = 50) {
        let path = `/api/export/logs?limit=${limit}`;
        if (algoType) path += `&algorithm_type=${algoType}`;
        return this.get(path);
    },
    exportLog(logId, format = 'json') { return this.get(`/api/export/export/${logId}?format=${format}`); },

    // === 用户测试数据 ===
    saveTestCase(algoType, name, inputData) {
        return this.post(`/api/compare/save-test-case?algorithm_type=${algoType}&name=${encodeURIComponent(name)}&input_data=${encodeURIComponent(inputData)}`);
    },
    getSavedTestCases(algoType) {
        let path = '/api/compare/test-cases';
        if (algoType) path += `?algorithm_type=${algoType}`;
        return this.get(path);
    },
    deleteTestCase(id) { return this.delete(`/api/compare/test-cases/${id}`); },
};
