/**
 * 算法可视化系统 - 主应用逻辑
 */

const App = {
    algorithmList: {},
    currentAlgorithmId: null,
    algorithmInfo: null,
    currentInputData: null,

    /** 算法元数据映射 */
    algoMeta: {
        bubble_sort: { icon: '🫧', cat: '排序算法', diff: '低-中' },
        quick_sort: { icon: '⚡', cat: '排序算法', diff: '中' },
        mst: { icon: '🕸️', cat: '图算法', diff: '中' },
        huffman: { icon: '🌳', cat: '树结构', diff: '中' },
        hanoi: { icon: '🗼', cat: '递归', diff: '中-高' },
        graph_coloring: { icon: '🎨', cat: '回溯', diff: '中-高' },
    },

    /** ====== 初始化 ====== */
    async init() {
        // 检查登录状态
        if (!API.getToken()) {
            window.location.href = '/login.html';
            return;
        }

        // 验证Token
        try {
            const user = await API.getMe();
            document.getElementById('usernameDisplay').textContent = user.username;
        } catch (e) {
            window.location.href = '/login.html';
            return;
        }

        // 加载算法列表
        await this.loadAlgorithms();

        // 绑定事件
        this.bindEvents();

        // 初始化AI对话
        AIChat.init();

        // 初始化对比视图 & 知识库
        CompareView.init();
        KnowledgeView.init();

        // 暴露到window供其他模块使用
        window.appState = this;
    },

    /** ====== 加载算法列表 ====== */
    async loadAlgorithms() {
        try {
            const data = await API.getAlgorithms();
            this.algorithmList = data.algorithms || {};
            this.renderAlgorithmList();
        } catch (e) {
            this.showToast('加载算法列表失败: ' + e.message, 'error');
        }
    },

    /** 渲染算法选择列表 */
    renderAlgorithmList() {
        const container = document.getElementById('algoList');
        container.innerHTML = '';

        // 按分类分组
        const categories = {};
        for (const [id, info] of Object.entries(this.algorithmList)) {
            const cat = info.category || '其他';
            if (!categories[cat]) categories[cat] = [];
            categories[cat].push({ id, ...info });
        }

        for (const [cat, algos] of Object.entries(categories)) {
            const catHeader = document.createElement('div');
            catHeader.style.cssText = 'font-size:11px;color:#999;padding:8px 4px 4px;font-weight:600;text-transform:uppercase;';
            catHeader.textContent = cat;
            container.appendChild(catHeader);

            algos.forEach(algo => {
                const item = document.createElement('div');
                item.className = 'algo-item';
                item.dataset.algoId = algo.id;
                item.innerHTML = `
                    <div class="algo-item-icon">${(this.algoMeta[algo.id] || {}).icon || '📌'}</div>
                    <div class="algo-item-info">
                        <div class="algo-item-name">${algo.name}</div>
                        <div class="algo-item-cat">${algo.difficulty || ''}</div>
                    </div>
                `;
                item.addEventListener('click', () => this.selectAlgorithm(algo.id));
                container.appendChild(item);
            });
        }
    },

    /** ====== 选择算法 ====== */
    async selectAlgorithm(algoId) {
        this.currentAlgorithmId = algoId;

        // 高亮选中
        document.querySelectorAll('.algo-item').forEach(el => el.classList.remove('active'));
        document.querySelector(`.algo-item[data-algo-id="${algoId}"]`)?.classList.add('active');

        try {
            // 加载算法详情
            const detail = await API.getAlgorithm(algoId);
            this.algorithmInfo = detail;

            // 更新信息栏
            document.getElementById('algoNameDisplay').textContent =
                `${detail.name} - ${detail.description}`;
            document.getElementById('timeBadge').textContent = `时间复杂度: ${detail.time_complexity}`;
            document.getElementById('spaceBadge').textContent = `空间复杂度: ${detail.space_complexity}`;
            document.getElementById('diffBadge').textContent = `难度: ${detail.difficulty}`;

            // 渲染输入面板
            this.renderInputPanel(algoId, detail);

            // 加载测试用例
            this.loadTestCases(algoId);

            // 重置可视化
            PlaybackController.stopAutoPlay();
            PlaybackController.updateControlButtons(false);
            VizRenderer.hideAll();
            document.getElementById('vizPlaceholder').style.display = 'block';
            document.getElementById('resultPanel').style.display = 'none';
            document.getElementById('stepDescription').textContent = '选择算法并输入数据后，点击"开始运行"';
        } catch (e) {
            this.showToast('加载算法详情失败: ' + e.message, 'error');
        }
    },

    /** ====== 渲染输入面板 ====== */
    renderInputPanel(algoId, detail) {
        const panel = document.getElementById('inputPanel');
        const fields = detail.input_fields || [];

        let html = '<div class="input-panel">';

        fields.forEach(field => {
            html += `<label>${field.label}</label>`;

            if (field.type === 'array') {
                html += `<textarea id="input_${field.name}" placeholder="${field.placeholder || ''}" rows="2"></textarea>`;
            } else if (field.type === 'number') {
                const min = field.min || 0;
                const max = field.max || 100;
                html += `<input type="number" id="input_${field.name}" min="${min}" max="${max}" value="${min}">`;
                html += `<span style="font-size:10px;color:#999;">范围: ${min}-${max}</span>`;
            } else if (field.type === 'matrix') {
                html += `<textarea id="input_${field.name}" placeholder="输入邻接矩阵，每行用逗号分隔，行间用换行分隔" rows="4"></textarea>`;
            } else if (field.type === 'string') {
                html += `<input type="text" id="input_${field.name}" placeholder="${field.placeholder || ''}">`;
            }
            html += `<div class="input-error" id="error_${field.name}"></div>`;
        });

        html += '<div class="input-error" id="inputGeneralError"></div>';
        html += '</div>';
        panel.innerHTML = html;
    },

    /** ====== 加载测试用例 ====== */
    async loadTestCases(algoId) {
        const container = document.getElementById('testCaseList');
        container.innerHTML = '<div style="font-size:12px;color:#999;">加载中...</div>';

        try {
            const data = await API.getTestCases(algoId);
            const cases = data.test_cases || [];

            container.innerHTML = '';
            cases.forEach((tc, index) => {
                const item = document.createElement('div');
                item.className = 'test-case-item';
                item.innerHTML = `<strong>${tc.name}</strong><br><small>${tc.description}</small>`;
                item.addEventListener('click', () => this.loadTestCase(algoId, tc, index));
                container.appendChild(item);
            });

            // 加载用户保存的测试数据
            this.loadSavedTestCases(algoId);
        } catch (e) {
            container.innerHTML = '<div style="font-size:12px;color:#f44336;">加载失败</div>';
        }
    },

    /** 加载用户保存的测试数据 */
    async loadSavedTestCases(algoId) {
        try {
            const data = await API.getSavedTestCases(algoId);
            const cases = data.test_cases || [];
            const container = document.getElementById('testCaseList');

            cases.forEach(tc => {
                const item = document.createElement('div');
                item.className = 'test-case-item';
                item.style.borderLeft = '3px solid #4CAF50';
                item.innerHTML = `<strong>💾 ${tc.name}</strong><br><small>自定义数据</small>`;
                item.addEventListener('click', () => {
                    try {
                        const parsed = JSON.parse(tc.input_data);
                        this.fillInputData(algoId, parsed);
                    } catch (e) {
                        this.showToast('数据解析失败', 'error');
                    }
                });
                container.appendChild(item);
            });
        } catch (e) {
            // 忽略
        }
    },

    /** 加载测试用例到输入框 */
    loadTestCase(algoId, testCase, index) {
        const data = testCase.data;
        this.fillInputData(algoId, data);

        // 自动运行
        this.runAlgorithm(algoId, data, index + 1);
    },

    /** 填充输入数据到表单 */
    fillInputData(algoId, data) {
        if (!data) return;

        if (algoId === 'bubble_sort' || algoId === 'quick_sort') {
            const arr = data.array || [];
            const textarea = document.getElementById('input_array');
            if (textarea) textarea.value = arr.join(',');
        } else if (algoId === 'mst' || algoId === 'graph_coloring') {
            if (data.edges) {
                const textarea = document.getElementById('input_edges');
                if (textarea) {
                    textarea.value = data.edges.map(row => row.join(',')).join('\n');
                }
            }
            if (data.vertices) {
                const input = document.getElementById('input_vertices');
                if (input) input.value = data.vertices;
            }
            if (data.colors) {
                const input = document.getElementById('input_colors');
                if (input) input.value = data.colors;
            }
        } else if (algoId === 'huffman') {
            if (data.chars) {
                const input = document.getElementById('input_chars');
                if (input) input.value = data.chars.join(',');
            }
            if (data.freqs) {
                const input = document.getElementById('input_freqs');
                if (input) input.value = data.freqs.join(',');
            }
        } else if (algoId === 'hanoi') {
            const input = document.getElementById('input_disks');
            if (input && data.disks) input.value = data.disks;
        }
    },

    /** ====== 解析输入数据 ====== */
    parseInputData(algoId) {
        const errors = [];
        const result = {};

        document.querySelectorAll('.input-error').forEach(el => el.textContent = '');

        if (algoId === 'bubble_sort' || algoId === 'quick_sort') {
            const raw = document.getElementById('input_array')?.value.trim();
            if (!raw) {
                errors.push('请输入数组数据');
            } else {
                const arr = raw.split(/[,，\s]+/).map(s => Number(s.trim())).filter(n => !isNaN(n));
                if (arr.length < 2) {
                    errors.push('至少需要2个数字');
                } else if (arr.length > 50) {
                    errors.push('数组长度不能超过50');
                } else {
                    result.array = arr;
                }
            }
            return { data: result, errors };

        } else if (algoId === 'mst') {
            const vRaw = document.getElementById('input_vertices')?.value;
            const v = parseInt(vRaw);
            if (isNaN(v) || v < 3 || v > 10) {
                errors.push('顶点数必须在3-10之间');
                return { data: result, errors };
            }
            result.vertices = v;

            const matrixRaw = document.getElementById('input_edges')?.value.trim();
            if (!matrixRaw) {
                errors.push('请输入邻接矩阵');
                return { data: result, errors };
            }
            const rows = matrixRaw.split('\n').filter(r => r.trim());
            if (rows.length !== v) {
                errors.push(`邻接矩阵需要${v}行，当前${rows.length}行`);
                return { data: result, errors };
            }

            const matrix = rows.map(row =>
                row.split(/[,，\s]+/).map(s => parseInt(s.trim()) || 0)
            );
            let valid = true;
            for (let i = 0; i < v && valid; i++) {
                if (matrix[i].length !== v) {
                    errors.push(`第${i + 1}行需要${v}个元素`);
                    valid = false;
                }
                for (let j = 0; j < v && valid; j++) {
                    if (matrix[i][j] !== matrix[j][i]) {
                        errors.push(`矩阵不对称: [${i}][${j}] ≠ [${j}][${i}]`);
                        valid = false;
                    }
                }
            }
            result.edges = matrix;
            return { data: result, errors };

        } else if (algoId === 'graph_coloring') {
            const vRaw = document.getElementById('input_vertices')?.value;
            const v = parseInt(vRaw);
            if (isNaN(v) || v < 3 || v > 10) {
                errors.push('顶点数必须在3-10之间');
                return { data: result, errors };
            }
            result.vertices = v;

            const cRaw = document.getElementById('input_colors')?.value;
            const m = parseInt(cRaw);
            if (isNaN(m) || m < 2 || m > 6) {
                errors.push('颜色数必须在2-6之间');
                return { data: result, errors };
            }
            result.colors = m;

            const matrixRaw = document.getElementById('input_edges')?.value.trim();
            if (!matrixRaw) {
                errors.push('请输入邻接矩阵');
                return { data: result, errors };
            }
            const rows = matrixRaw.split('\n').filter(r => r.trim());
            if (rows.length !== v) {
                errors.push(`邻接矩阵需要${v}行`);
                return { data: result, errors };
            }
            const matrix = rows.map(row =>
                row.split(/[,，\s]+/).map(s => {
                    const num = parseInt(s.trim());
                    return (num === 1) ? 1 : 0;
                })
            );
            for (let i = 0; i < v; i++) {
                if (matrix[i].length !== v) {
                    errors.push(`第${i + 1}行需要${v}个元素`);
                }
            }
            result.edges = matrix;
            return { data: result, errors };

        } else if (algoId === 'huffman') {
            const charsRaw = document.getElementById('input_chars')?.value.trim();
            const freqsRaw = document.getElementById('input_freqs')?.value.trim();

            if (!charsRaw) { errors.push('请输入字符'); return { data: result, errors }; }
            if (!freqsRaw) { errors.push('请输入频率'); return { data: result, errors }; }

            const chars = charsRaw.split(/[,，\s]+/).filter(s => s);
            const freqs = freqsRaw.split(/[,，\s]+/).map(s => Number(s.trim())).filter(n => !isNaN(n) && n > 0);

            if (chars.length < 2) errors.push('至少需要2个字符');
            if (chars.length > 26) errors.push('最多26个字符');
            if (chars.length !== freqs.length) {
                errors.push(`字符数(${chars.length})与频率数(${freqs.length})不匹配`);
            }

            result.chars = chars;
            result.freqs = freqs;
            return { data: result, errors };

        } else if (algoId === 'hanoi') {
            const nRaw = document.getElementById('input_disks')?.value;
            const n = parseInt(nRaw);
            if (isNaN(n) || n < 2 || n > 8) {
                errors.push('盘子数量必须在2-8之间');
            }
            result.disks = n;
            return { data: result, errors };
        }

        return { data: result, errors: ['未知算法类型'] };
    },

    /** ====== 运行算法 ====== */
    async runAlgorithm(algoId, inputData, testCaseIndex = 0) {
        // 验证
        if (!inputData) {
            const parsed = this.parseInputData(algoId);
            if (parsed.errors.length > 0) {
                parsed.errors.forEach(err => this.showToast(err, 'error'));
                document.getElementById('inputGeneralError').textContent = parsed.errors.join('; ');
                return;
            }
            inputData = parsed.data;
        }

        this.currentInputData = inputData;

        try {
            document.getElementById('btnRunSidebar').disabled = true;
            this.showToast('正在执行算法...', 'info');

            const response = await API.runAlgorithm(algoId, inputData);

            // 初始化播放控制器
            PlaybackController.init(algoId, response.steps, response);

            // 保存执行日志
            this.saveExecutionLog(algoId, inputData, testCaseIndex, response);

            this.showToast(`算法执行完成！共 ${response.total_steps} 步`, 'success');
        } catch (e) {
            this.showToast(`执行失败: ${e.message}`, 'error');
            document.getElementById('btnRunSidebar').disabled = false;
        }
    },

    /** 保存执行日志 */
    async saveExecutionLog(algoId, inputData, testCaseIndex, response) {
        try {
            await API.saveLog({
                algorithm_type: algoId,
                input_data: JSON.stringify(inputData),
                is_test_case: testCaseIndex > 0 ? 1 : 0,
                test_case_index: testCaseIndex || null,
                total_steps: response.total_steps,
                execution_time_ms: response.execution_time_ms,
            });
        } catch (e) {
            // 静默失败，不影响主流程
        }
    },

    /** ====== 生成随机数据 ====== */
    async generateRandomData() {
        if (!this.currentAlgorithmId) {
            this.showToast('请先选择算法', 'warning');
            return;
        }

        try {
            const data = await API.getRandomData(this.currentAlgorithmId);
            this.fillInputData(this.currentAlgorithmId, data.data);
            this.showToast('随机数据已生成', 'success');
        } catch (e) {
            this.showToast('生成随机数据失败', 'error');
        }
    },

    /** ====== 保存自定义测试数据 ====== */
    async saveTestCase() {
        if (!this.currentAlgorithmId) {
            this.showToast('请先选择算法', 'warning');
            return;
        }

        const parsed = this.parseInputData(this.currentAlgorithmId);
        if (parsed.errors.length > 0) {
            this.showToast('请先输入有效数据', 'warning');
            return;
        }

        const name = prompt('为这组测试数据命名:');
        if (!name) return;

        try {
            await API.saveTestCase(
                this.currentAlgorithmId,
                name,
                JSON.stringify(parsed.data)
            );
            this.showToast('测试数据保存成功！', 'success');
            this.loadTestCases(this.currentAlgorithmId);
        } catch (e) {
            this.showToast('保存失败: ' + e.message, 'error');
        }
    },

    /** ====== 导出日志 ====== */
    async exportLog() {
        try {
            const data = await API.getLogs(this.currentAlgorithmId, 1);
            if (data.logs.length === 0) {
                this.showToast('没有可导出的日志', 'warning');
                return;
            }

            const logId = data.logs[0].id;
            this.downloadXlsx(`/api/export/export/${logId}`, `algo_log_${logId}.xlsx`);
        } catch (e) {
            this.showToast('导出失败: ' + e.message, 'error');
        }
    },

    /** 下载xlsx文件 */
    async downloadXlsx(urlPath, filename) {
        const token = API.getToken();
        const resp = await fetch(`${API_BASE}${urlPath}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (resp.ok) {
            const blob = await resp.blob();
            const downloadUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(downloadUrl);
            this.showToast('日志导出成功（.xlsx）！', 'success');
        } else {
            this.showToast('导出失败', 'error');
        }
    },

    /** ====== 加载执行日志视图 ====== */
    async loadHistoryView() {
        try {
            const filter = document.getElementById('historyFilter')?.value || '';
            const data = await API.getLogs(filter || null, 100);
            const tbody = document.getElementById('historyTableBody');
            tbody.innerHTML = '';

            const algoNames = {
                bubble_sort: '冒泡排序', quick_sort: '快速排序',
                mst: '最小生成树', huffman: '哈夫曼树',
                hanoi: '汉诺塔', graph_coloring: '图着色',
            };

            data.logs.forEach(log => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${log.id}</td>
                    <td>${algoNames[log.algorithm_type] || log.algorithm_type}</td>
                    <td><small>${(log.input_data || '').substring(0, 50)}...</small></td>
                    <td>${log.total_steps}</td>
                    <td>${log.execution_time_ms || '-'}</td>
                    <td>${log.created_at ? new Date(log.created_at).toLocaleString() : '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline export-one-btn" data-id="${log.id}">导出</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // 绑定导出按钮
            document.querySelectorAll('.export-one-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.target.dataset.id;
                    this.downloadXlsx(`/api/export/export/${id}`, `algo_log_${id}.xlsx`);
                });
            });
        } catch (e) {
            this.showToast('加载日志失败: ' + e.message, 'error');
        }
    },

    /** ====== 批量导出 ====== */
    async exportAllLogs() {
        const filter = document.getElementById('historyFilter')?.value || '';
        const query = filter ? `?algorithm_type=${filter}` : '';
        this.downloadXlsx(`/api/export/export-all${query}`, 'algo_logs_all.xlsx');
    },

    /** ====== Toast提示 ====== */
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    /** ====== 切换视图 ====== */
    switchView(view) {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelector(`.nav-btn[data-view="${view}"]`)?.classList.add('active');

        const mainContainer = document.querySelector('.main-container');
        const compareView = document.getElementById('compareView');
        const historyView = document.getElementById('historyView');
        const knowledgeView = document.getElementById('knowledgeView');

        // 隐藏所有视图
        [compareView, historyView, knowledgeView].forEach(v => v?.classList.add('hidden'));

        if (view === 'visualizer') {
            mainContainer.style.display = 'flex';
        } else if (view === 'compare') {
            mainContainer.style.display = 'none';
            CompareView.show();
        } else if (view === 'knowledge') {
            mainContainer.style.display = 'none';
            KnowledgeView.show();
        } else if (view === 'history') {
            mainContainer.style.display = 'none';
            historyView.classList.remove('hidden');
            this.loadHistoryView();
        }
    },

    /** ====== 绑定所有事件 ====== */
    bindEvents() {
        // 导航切换
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchView(btn.dataset.view));
        });

        // 运行按钮（侧边栏）
        const runHandler = () => {
            if (this.currentAlgorithmId) {
                this.runAlgorithm(this.currentAlgorithmId, null);
            } else {
                this.showToast('请先选择算法', 'warning');
            }
        };
        document.getElementById('btnRunSidebar').addEventListener('click', runHandler);

        // 控制按钮
        document.getElementById('btnStep').addEventListener('click', () => PlaybackController.nextStep());
        document.getElementById('btnStepBack').addEventListener('click', () => PlaybackController.prevStep());
        document.getElementById('btnAutoPlay').addEventListener('click', () => PlaybackController.startAutoPlay());
        document.getElementById('btnPause').addEventListener('click', () => PlaybackController.stopAutoPlay());
        document.getElementById('btnReset').addEventListener('click', () => PlaybackController.reset());
        document.getElementById('btnJump').addEventListener('click', () => {
            const idx = parseInt(document.getElementById('stepJumpInput').value);
            PlaybackController.jumpToStep(idx);
        });

        // 速度控制
        document.getElementById('speedSlider').addEventListener('input', (e) => {
            PlaybackController.setSpeed(parseFloat(e.target.value));
        });

        // 随机数据
        document.getElementById('randomDataBtn').addEventListener('click', () => this.generateRandomData());

        // 保存测试数据
        document.getElementById('saveTestCaseBtn').addEventListener('click', () => this.saveTestCase());

        // 导出
        document.getElementById('exportBtn').addEventListener('click', () => this.exportLog());

        // 教程模式
        document.getElementById('tutorialMode').addEventListener('change', (e) => {
            PlaybackController.toggleTutorialMode(e.target.checked);
        });

        // 退出登录
        document.getElementById('logoutBtn').addEventListener('click', () => {
            API.setToken('');
            window.location.href = '/login.html';
        });

        // 对比视图关闭
        document.getElementById('compareCloseBtn').addEventListener('click', () => {
            CompareView.hide();
            this.switchView('visualizer');
        });

        // 日志视图关闭
        document.getElementById('historyCloseBtn').addEventListener('click', () => {
            this.switchView('visualizer');
        });

        // 批量导出
        document.getElementById('exportAllBtn').addEventListener('click', () => this.exportAllLogs());

        // 日志筛选
        document.getElementById('historyFilter').addEventListener('change', () => this.loadHistoryView());

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            switch (e.key) {
                case 'ArrowRight': PlaybackController.nextStep(); break;
                case 'ArrowLeft': PlaybackController.prevStep(); break;
                case ' ': e.preventDefault(); PlaybackController.isPlaying ?
                    PlaybackController.stopAutoPlay() : PlaybackController.startAutoPlay(); break;
                case 'r': PlaybackController.reset(); break;
            }
        });
    },
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => App.init());
