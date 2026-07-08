/**
 * 算法可视化系统 - 知识库模块
 */

const KnowledgeView = {
    init() {
        document.getElementById('knowledgeCloseBtn').addEventListener('click', () => this.hide());

        // 绑定目录点击事件
        document.querySelectorAll('.knowledge-nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const algoId = item.dataset.algoId;
                const title = item.querySelector('.kni-cat')?.parentElement?.querySelector('div:first-child')?.textContent || algoId;
                this.loadArticle(algoId, title);
            });
        });
    },

    show() {
        document.getElementById('knowledgeView').classList.remove('hidden');
        document.querySelector('.main-container').style.display = 'none';
        document.getElementById('compareView').classList.add('hidden');
        document.getElementById('historyView').classList.add('hidden');
    },

    hide() {
        document.getElementById('knowledgeView').classList.add('hidden');
        document.querySelector('.main-container').style.display = 'flex';
    },

    async loadArticle(algoId, title) {
        // 高亮选中
        document.querySelectorAll('.knowledge-nav-item').forEach(el => el.classList.remove('active'));
        document.querySelector(`.knowledge-nav-item[data-algo-id="${algoId}"]`)?.classList.add('active');

        const content = document.getElementById('knowledgeContent');
        content.innerHTML = '<div class="knowledge-placeholder"><p>加载中...</p></div>';

        try {
            const data = await API.get(`/api/knowledge/${algoId}`);
            this.renderArticle(content, data);
        } catch (e) {
            content.innerHTML = `<div class="knowledge-placeholder"><p>加载失败: ${e.message}</p><p style="font-size:12px;color:#999;">请确认后端服务已启动</p></div>`;
        }
    },

    renderArticle(container, data) {
        let html = '<div class="knowledge-article">';
        html += `<h2>${data.title}</h2>`;
        html += `<div class="kcat">${data.category}</div>`;

        html += `<h3>📖 算法概述</h3>`;
        html += this.renderMarkdown(data.overview);

        html += `<h3>🖥️ 使用指南</h3>`;
        html += this.renderMarkdown(data.how_to_use);

        html += `<h3>📝 例题解析</h3>`;
        (data.examples || []).forEach((ex, i) => {
            html += `<div class="example-card">`;
            html += `<h4><span class="step-number">${i + 1}</span> ${ex.title}</h4>`;
            html += `<p><strong>题目：</strong>${ex.question}</p>`;
            if (ex.steps && ex.steps.length > 0) {
                html += `<div class="example-steps"><strong>解题步骤：</strong>`;
                ex.steps.forEach(step => {
                    html += `<div class="example-step">${step}</div>`;
                });
                html += `</div>`;
            }
            if (ex.answer) {
                html += `<div class="example-answer">✅ 答案：${ex.answer}</div>`;
            }
            html += `</div>`;
        });

        html += '</div>';
        container.innerHTML = html;
    },

    renderMarkdown(md) {
        if (!md) return '';
        return md
            .replace(/### (.+)/g, '<h4>$1</h4>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/^- (.+)/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
    }
};
