/**
 * 算法可视化系统 - 登录/注册
 */

const API_BASE = 'http://localhost:8001';

function initParticles() {
    const container = document.getElementById('particles');
    for (let i = 0; i < 60; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 4 + 1.5;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = Math.random() * 100 + '%';
        p.style.animationDuration = (Math.random() * 12 + 8) + 's';
        p.style.animationDelay = Math.random() * 10 + 's';
        container.appendChild(p);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initParticles();

    // 已登录则跳转
    const token = localStorage.getItem('algo_viz_token');
    if (token) {
        fetch(`${API_BASE}/api/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => { if (r.ok) window.location.href = '/index.html'; }).catch(() => {});
    }

    // Tab切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const tab = btn.dataset.tab;
            document.getElementById('loginForm').classList.toggle('hidden', tab !== 'login');
            document.getElementById('registerForm').classList.toggle('hidden', tab !== 'register');
            document.getElementById('loginError').textContent = '';
            document.getElementById('regError').textContent = '';
        });
    });

    // 登录
    document.getElementById('loginBtn').addEventListener('click', async () => {
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;
        const errorEl = document.getElementById('loginError');
        errorEl.textContent = '';

        if (!username) { errorEl.textContent = '请输入用户名'; return; }
        if (!password) { errorEl.textContent = '请输入密码'; return; }

        const btn = document.getElementById('loginBtn');
        btn.disabled = true; btn.textContent = '登录中...';

        try {
            const resp = await fetch(`${API_BASE}/api/auth/login`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await resp.json();
            if (resp.ok) {
                localStorage.setItem('algo_viz_token', data.access_token);
                window.location.href = '/index.html';
            } else {
                errorEl.textContent = data.detail || '登录失败';
            }
        } catch (e) {
            errorEl.textContent = '网络错误，请检查服务器连接';
        } finally {
            btn.disabled = false; btn.textContent = '登 录';
        }
    });

    // 注册
    document.getElementById('registerBtn').addEventListener('click', async () => {
        const username = document.getElementById('regUsername').value.trim();
        const password = document.getElementById('regPassword').value;
        const passwordConfirm = document.getElementById('regPasswordConfirm').value;
        const errorEl = document.getElementById('regError');
        errorEl.textContent = '';

        if (!username) { errorEl.textContent = '请输入用户名'; return; }
        if (username.length < 3) { errorEl.textContent = '用户名至少3个字符'; return; }
        if (username.length > 50) { errorEl.textContent = '用户名最多50个字符'; return; }
        if (!password) { errorEl.textContent = '请输入密码'; return; }
        if (password.length < 6) { errorEl.textContent = '密码至少6个字符'; return; }
        if (password !== passwordConfirm) { errorEl.textContent = '两次密码不一致'; return; }

        const btn = document.getElementById('registerBtn');
        btn.disabled = true; btn.textContent = '注册中...';

        try {
            const resp = await fetch(`${API_BASE}/api/auth/register`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await resp.json();
            if (resp.ok) {
                localStorage.setItem('algo_viz_token', data.access_token);
                window.location.href = '/index.html';
            } else {
                errorEl.textContent = data.detail || '注册失败';
            }
        } catch (e) {
            errorEl.textContent = '网络错误，请检查服务器连接';
        } finally {
            btn.disabled = false; btn.textContent = '注 册';
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const activeTab = document.querySelector('.tab-btn.active');
            if (activeTab?.dataset.tab === 'login') document.getElementById('loginBtn').click();
            else document.getElementById('registerBtn').click();
        }
    });
});
