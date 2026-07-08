/**
 * 算法可视化系统 - 执行控制模块
 */

const PlaybackController = {
    steps: [],
    currentStepIndex: 0,
    isPlaying: false,
    playInterval: null,
    speed: 1,           // 倍速 (0.5x ~ 5x)
    baseInterval: 800,  // 1x速度对应800ms
    algoId: null,
    tutorialMode: false,
    allStepsData: null, // 完整API响应数据

    /** 初始化 */
    init(algoId, stepsData, apiResponse) {
        this.steps = stepsData.steps || [];
        this.currentStepIndex = 0;
        this.isPlaying = false;
        this.algoId = algoId;
        this.allStepsData = apiResponse;
        this.stopAutoPlay();

        // 更新UI
        this.updateUI();
        this.goToStep(0);
        this.updateControlButtons(true);
        this.updateResultPanel(null);
    },

    /** 跳转到指定步骤 */
    goToStep(index) {
        if (index < 0) index = 0;
        if (index >= this.steps.length) index = this.steps.length - 1;

        this.currentStepIndex = index;
        const step = this.steps[index];

        // 渲染可视化
        VizRenderer.render(this.algoId, step, this.steps, index);

        // 更新步骤说明
        this.updateStepDescription(step);

        // 更新进度
        this.updateProgress();

        // 如果开启教程模式，请求AI解释
        if (this.tutorialMode && step) {
            this.requestAIExplanation(step);
        }

        // 最后一步显示结果
        if (index === this.steps.length - 1 && this.allStepsData) {
            this.updateResultPanel(this.allStepsData);
        }
    },

    /** 下一步 */
    nextStep() {
        if (this.currentStepIndex < this.steps.length - 1) {
            this.goToStep(this.currentStepIndex + 1);
            return true;
        }
        return false;
    },

    /** 上一步（回退） */
    prevStep() {
        if (this.currentStepIndex > 0) {
            this.goToStep(this.currentStepIndex - 1);
            return true;
        }
        return false;
    },

    /** 自动播放 */
    startAutoPlay() {
        if (this.isPlaying) return;
        if (this.currentStepIndex >= this.steps.length - 1) {
            this.goToStep(0);
        }
        this.isPlaying = true;
        this.updateControlButtons(true);

        const intervalMs = this.baseInterval / this.speed;
        this.playInterval = setInterval(() => {
            if (!this.nextStep()) {
                this.stopAutoPlay();
            }
        }, intervalMs);
    },

    /** 暂停 */
    stopAutoPlay() {
        this.isPlaying = false;
        if (this.playInterval) {
            clearInterval(this.playInterval);
            this.playInterval = null;
        }
        this.updateControlButtons(true);
    },

    /** 重置 */
    reset() {
        this.stopAutoPlay();
        this.goToStep(0);
        this.updateResultPanel(null);
    },

    /** 设置速度 */
    setSpeed(speed) {
        this.speed = speed;
        document.getElementById('speedLabel').textContent = speed + 'x';
        if (this.isPlaying) {
            this.stopAutoPlay();
            this.startAutoPlay();
        }
    },

    /** 跳转到指定步骤 */
    jumpToStep(index) {
        if (index >= 0 && index < this.steps.length) {
            this.stopAutoPlay();
            this.goToStep(index);
        }
    },

    /** 更新UI */
    updateUI() {
        document.getElementById('stepJumpInput').max = this.steps.length - 1;
        document.getElementById('stepJumpInput').value = this.currentStepIndex;
        this.updateProgress();
    },

    /** 更新进度条 */
    updateProgress() {
        const total = this.steps.length;
        const current = this.currentStepIndex + 1;
        const percent = total > 0 ? (current / total) * 100 : 0;

        document.getElementById('progressBar').style.width = percent + '%';
        document.getElementById('stepCounter').textContent = `步骤: ${current} / ${total}`;

        if (this.allStepsData && this.allStepsData.execution_time_ms !== undefined) {
            document.getElementById('executionTime').textContent =
                `执行耗时: ${this.allStepsData.execution_time_ms}ms`;
        }

        document.getElementById('stepJumpInput').value = this.currentStepIndex;
        document.getElementById('stepJumpInput').max = total - 1;
    },

    /** 更新步骤描述 */
    updateStepDescription(step) {
        const descEl = document.getElementById('stepDescription');
        if (step) {
            descEl.textContent = `[步骤 ${step.step_index}] ${step.step_type.toUpperCase()}: ${step.description}`;
        }
        // 隐藏AI解释（等新请求）
        document.getElementById('aiExplanation').style.display = 'none';
    },

    /** 请求AI步骤解释 */
    async requestAIExplanation(step) {
        const aiExp = document.getElementById('aiExplanation');
        const aiText = document.getElementById('aiExplanationText');
        aiExp.style.display = 'block';
        aiText.textContent = 'AI正在分析此步骤...';

        try {
            const data = await API.post('/api/ai/chat/explain-step', {
                algorithm_type: this.algoId,
                step_description: step.description,
            });
            aiText.textContent = (data && data.explanation) ? data.explanation : '无法获取AI解释';
        } catch (e) {
            aiText.textContent = 'AI解释服务暂不可用';
        }
    },

    /** 更新结果面板 */
    updateResultPanel(apiResponse) {
        const panel = document.getElementById('resultPanel');
        const content = document.getElementById('resultContent');

        if (!apiResponse || !apiResponse.result) {
            panel.style.display = 'none';
            return;
        }

        panel.style.display = 'block';
        const result = apiResponse.result;
        let html = `<div style="font-size:13px;line-height:1.8;">`;
        html += `<strong>总步数:</strong> ${apiResponse.total_steps}<br>`;
        html += `<strong>时间复杂度:</strong> ${apiResponse.time_complexity}<br>`;
        html += `<strong>空间复杂度:</strong> ${apiResponse.space_complexity}<br>`;

        // 算法特定结果
        switch (this.algoId) {
            case 'bubble_sort':
                html += `<strong>排序结果:</strong> [${result.sorted_array}]<br>`;
                html += `<strong>比较次数:</strong> ${result.comparisons}<br>`;
                html += `<strong>交换次数:</strong> ${result.swaps}<br>`;
                break;
            case 'quick_sort':
                html += `<strong>排序结果:</strong> [${result.sorted_array}]<br>`;
                break;
            case 'mst':
                html += `<strong>MST总权重:</strong> ${result.total_weight}<br>`;
                html += `<strong>MST边数:</strong> ${(result.mst_edges || []).length}<br>`;
                break;
            case 'huffman':
                html += `<strong>编码表:</strong><br>`;
                const codes = result.codes || {};
                for (const [ch, code] of Object.entries(codes)) {
                    html += `&nbsp;&nbsp;'${ch}': ${code}<br>`;
                }
                html += `<strong>WPL:</strong> ${result.wpl}<br>`;
                break;
            case 'hanoi':
                html += `<strong>移动步数:</strong> ${result.move_count}<br>`;
                html += `<strong>理论最少:</strong> ${result.optimal_moves}<br>`;
                html += `<strong>是否最优:</strong> ${result.is_optimal ? '✅ 是' : '❌ 否'}<br>`;
                break;
            case 'graph_coloring':
                html += `<strong>找到解数:</strong> ${result.solutions_count}<br>`;
                html += `<strong>回溯次数:</strong> ${result.backtrack_count}<br>`;
                html += `<strong>着色方案:</strong> ${JSON.stringify(result.solution)}<br>`;
                break;
        }

        html += `</div>`;
        content.innerHTML = html;
    },

    /** 更新控制按钮状态 */
    updateControlButtons(runEnabled) {
        const hasSteps = this.steps.length > 0;
        document.getElementById('btnRunSidebar').disabled = !runEnabled;
        document.getElementById('btnStep').disabled = !hasSteps || this.isPlaying;
        document.getElementById('btnStepBack').disabled = !hasSteps || this.currentStepIndex <= 0 || this.isPlaying;
        document.getElementById('btnAutoPlay').disabled = !hasSteps || this.isPlaying;
        document.getElementById('btnPause').disabled = !this.isPlaying;
        document.getElementById('btnReset').disabled = !hasSteps;
        document.getElementById('btnJump').disabled = !hasSteps;
        document.getElementById('stepJumpInput').disabled = !hasSteps;
        document.getElementById('exportBtn').disabled = !hasSteps;
    },

    /** 切换教程模式 */
    toggleTutorialMode(enabled) {
        this.tutorialMode = enabled;
        if (enabled && this.steps.length > 0) {
            this.requestAIExplanation(this.steps[this.currentStepIndex]);
        } else {
            document.getElementById('aiExplanation').style.display = 'none';
        }
    },
};
