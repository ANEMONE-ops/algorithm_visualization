/**
 * 算法可视化系统 - AI对话模块
 */

const AIChat = {
    conversationHistory: [],

    /** 初始化AI对话框事件 */
    init() {
        const sendBtn = document.getElementById('aiSendBtn');
        const input = document.getElementById('aiInput');

        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    },

    /** 发送消息 */
    async sendMessage() {
        const input = document.getElementById('aiInput');
        const message = input.value.trim();

        if (!message) return;

        // 添加用户消息到界面
        this.appendMessage('user', message);
        input.value = '';
        input.disabled = true;
        document.getElementById('aiSendBtn').disabled = true;

        // 获取当前算法上下文
        let algoContext = null;
        if (window.appState && window.appState.currentAlgorithm) {
            const algo = window.appState.algorithmInfo;
            if (algo) {
                algoContext = `算法: ${algo.name}, 分类: ${algo.category}, `
                    + `时间复杂度: ${algo.time_complexity}, 空间复杂度: ${algo.space_complexity}, `
                    + `描述: ${algo.description}`;
            }
        }

        // 添加加载提示
        const loadingId = this.appendMessage('bot', '⏳ 正在思考...');

        try {
            const data = await API.chat(message, algoContext, this.conversationHistory);

            // 移除加载提示
            this.removeMessage(loadingId);

            // 添加AI回复
            this.appendMessage('bot', data.reply);

            // 保存对话历史
            this.conversationHistory.push(
                { role: 'user', content: message },
                { role: 'assistant', content: data.reply }
            );

            // 限制历史长度
            if (this.conversationHistory.length > 20) {
                this.conversationHistory = this.conversationHistory.slice(-20);
            }
        } catch (e) {
            this.removeMessage(loadingId);
            this.appendMessage('bot', `⚠️ AI服务暂时不可用: ${e.message}\n\n建议查看算法详情面板获取帮助。`);
        }

        input.disabled = false;
        document.getElementById('aiSendBtn').disabled = false;
        input.focus();
    },

    /** 向聊天区域添加消息 */
    appendMessage(role, content) {
        const container = document.getElementById('aiChatMessages');
        const msgDiv = document.createElement('div');
        const id = 'ai-msg-' + Date.now();
        msgDiv.id = id;
        msgDiv.className = `ai-message ai-message-${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'ai-avatar';
        avatar.textContent = role === 'user' ? '👤' : '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-content';
        contentDiv.textContent = content;

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        container.appendChild(msgDiv);

        // 滚动到底部
        container.scrollTop = container.scrollHeight;

        return id;
    },

    /** 移除消息 */
    removeMessage(id) {
        const msg = document.getElementById(id);
        if (msg) msg.remove();
    },

    /** 清空对话 */
    clearHistory() {
        this.conversationHistory = [];
        const container = document.getElementById('aiChatMessages');
        container.innerHTML = `
            <div class="ai-message ai-message-bot">
                <div class="ai-avatar">🤖</div>
                <div class="ai-content">对话已清空。有什么可以帮你的？</div>
            </div>
        `;
    },
};
