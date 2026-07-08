/**
 * 算法可视化系统 - 算法对比模块（全图形化）
 */

const CompareView = {
    results: null,
    leftStepIndex: 0,
    rightStepIndex: 0,
    isPlaying: false,
    playInterval: null,

    init() {
        document.getElementById('compareRunBtn').addEventListener('click', () => this.runCompare());
        document.getElementById('compareCloseBtn').addEventListener('click', () => this.hide());
        document.getElementById('comparePlayBtn').addEventListener('click', () => this.togglePlay());
        document.getElementById('compareResetBtn').addEventListener('click', () => this.reset());
    },

    show() {
        document.getElementById('compareView').classList.remove('hidden');
        document.querySelector('.main-container').style.display = 'none';
        this.loadAlgorithmOptions();
    },

    hide() {
        this.stopPlay();
        document.getElementById('compareView').classList.add('hidden');
        document.querySelector('.main-container').style.display = 'flex';
    },

    async loadAlgorithmOptions() {
        try {
            const data = await API.get('/api/compare/algorithms');
            const algos = data.algorithms || [];
            [document.getElementById('compareAlgoA'), document.getElementById('compareAlgoB')].forEach(select => {
                select.innerHTML = '<option value="">-- 选择算法 --</option>';
                algos.forEach(a => {
                    const opt = document.createElement('option');
                    opt.value = a.id;
                    opt.textContent = `${a.name} (${a.category} | ${a.time_complexity})`;
                    select.appendChild(opt);
                });
            });
        } catch (e) {
            console.error(e);
        }
    },

    async runCompare() {
        const algoA = document.getElementById('compareAlgoA').value;
        const algoB = document.getElementById('compareAlgoB').value;
        if (!algoA || !algoB) { App.showToast('请选择两个算法', 'warning'); return; }
        if (algoA === algoB) { App.showToast('请选择两个不同的算法', 'warning'); return; }

        try {
            App.showToast('正在执行对比...', 'info');
            // 对比模块完全独立，不依赖可视化模块的数据
            const resp = await fetch(`${API_BASE}/api/compare/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${API.getToken()}` },
                body: JSON.stringify({ algo_a: algoA, algo_b: algoB }),
            });
            this.results = await resp.json();
            if (!resp.ok) throw new Error(this.results.detail || '对比失败');

            this.leftStepIndex = 0; this.rightStepIndex = 0;
            this.renderCompare();
            document.getElementById('comparePlayBtn').disabled = false;
            document.getElementById('compareResetBtn').disabled = false;
            App.showToast('对比执行完成！', 'success');
        } catch (e) {
            App.showToast(`对比失败: ${e.message}`, 'error');
        }
    },

    renderCompare() {
        if (!this.results?.algorithms || this.results.algorithms.length < 2) return;
        const left = this.results.algorithms[0];
        const right = this.results.algorithms[1];

        // 左侧
        document.querySelector('#compareLeft h4').textContent =
            `${left.algorithm_name} | ${left.time_complexity} | ${left.total_steps}步`;
        this.renderPane('compareLeft', left, this.leftStepIndex);

        // 右侧
        document.querySelector('#compareRight h4').textContent =
            `${right.algorithm_name} | ${right.time_complexity} | ${right.total_steps}步`;
        this.renderPane('compareRight', right, this.rightStepIndex);
    },

    /** 渲染单个对比面板 */
    renderPane(paneId, algoData, stepIdx) {
        const vizContainer = document.querySelector(`#${paneId} .compare-viz`);
        const infoContainer = document.querySelector(`#${paneId} .compare-info`);
        vizContainer.innerHTML = '';

        if (!algoData.steps?.steps || algoData.steps.steps.length === 0) {
            vizContainer.innerHTML = '<p style="padding:20px;color:#999;">无步骤数据</p>';
            return;
        }

        const step = algoData.steps.steps[stepIdx];
        const algoId = algoData.algorithm_id;
        const allSteps = algoData.steps.steps;

        // 根据算法类型选择渲染方式
        switch (algoId) {
            case 'bubble_sort':
            case 'quick_sort':
                this.renderCompareArray(vizContainer, step);
                break;
            case 'mst':
            case 'graph_coloring':
                this.renderCompareGraph(vizContainer, step, algoId);
                break;
            case 'huffman':
                this.renderCompareTree(vizContainer, step);
                break;
            case 'hanoi':
                this.renderCompareHanoi(vizContainer, step);
                break;
            default:
                vizContainer.innerHTML = `<div style="padding:20px;font-size:13px;white-space:pre-wrap;">[步骤 ${step.step_index}] ${step.description}</div>`;
        }

        infoContainer.innerHTML = `
            <strong>步骤:</strong> ${stepIdx + 1}/${algoData.total_steps}<br>
            <strong>当前操作:</strong> <span style="font-size:12px;">${step.description.substring(0, 80)}...</span><br>
            <strong>执行耗时:</strong> ${algoData.execution_time_ms}ms<br>
            <strong>结果:</strong> ${JSON.stringify(algoData.result).substring(0, 80)}
        `;
    },

    /** 数组对比渲染 */
    renderCompareArray(container, step) {
        const arr = step.data_snapshot || [];
        if (!arr.length) { container.innerHTML = '<p>等待数据...</p>'; return; }
        const maxVal = Math.max(...arr, 1);
        const hl = step.highlights || [];
        const hl2 = step.highlights_secondary || [];

        const wrapper = document.createElement('div');
        wrapper.style.cssText = 'display:flex;align-items:flex-end;justify-content:center;gap:4px;height:100%;padding:20px 10px;';

        arr.forEach((val, idx) => {
            const bar = document.createElement('div');
            const h = Math.max((val / maxVal) * 80, 8);
            let bg = '#4A90D9';
            if (hl.includes(idx)) bg = '#FF9800';
            if (hl2.includes(idx)) bg = '#4CAF50';

            bar.style.cssText = `height:${h}%;width:${Math.max(60/arr.length, 18)}px;border-radius:3px 3px 0 0;background:${bg};display:flex;align-items:flex-end;justify-content:center;transition:0.3s;`;
            if (hl.includes(idx)) bar.style.boxShadow = '0 0 10px rgba(255,152,0,0.7)';

            const lbl = document.createElement('span');
            lbl.style.cssText = 'font-size:9px;color:white;font-weight:600;margin-bottom:2px;';
            lbl.textContent = val;
            bar.appendChild(lbl);
            wrapper.appendChild(bar);
        });
        container.innerHTML = '';
        container.appendChild(wrapper);
    },

    /** 图对比渲染 (MST / 图着色) */
    renderCompareGraph(container, step, algoId) {
        const snap = step.data_snapshot;
        if (!snap || !snap.vertices) { container.innerHTML = '<p>等待图数据...</p>'; return; }

        const v = snap.vertices;
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%'); svg.setAttribute('height', '260');
        svg.setAttribute('viewBox', '-35 -35 320 280');
        container.appendChild(svg);

        const cx = 120, cy = 110, r = 90;
        const pos = {};
        for (let i = 0; i < v; i++) {
            const a = (2 * Math.PI * i) / v - Math.PI / 2;
            pos[i] = { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
        }

        const adj = snap.adjacency || {};
        const mstEdges = snap.mst_edges || [];
        const visited = snap.visited || [];
        const coloring = snap.coloring || [];
        const current = snap.current_vertex;
        const graphColors = ['#F44336','#4CAF50','#2196F3','#FFEB3B','#9C27B0','#FF9800'];

        // 边
        for (let i = 0; i < v; i++) {
            for (const [j, w] of (adj[i] || [])) {
                if (i < j) {
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', pos[i].x); line.setAttribute('y1', pos[i].y);
                    line.setAttribute('x2', pos[j].x); line.setAttribute('y2', pos[j].y);

                    const isMST = mstEdges.some(e => (e[0]===i&&e[1]===j)||(e[0]===j&&e[1]===i));
                    line.setAttribute('stroke', isMST ? '#4CAF50' : '#ccc');
                    line.setAttribute('stroke-width', isMST ? '2.5' : '1');
                    svg.appendChild(line);

                    if (w && w > 0) {
                        const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                        t.setAttribute('x', (pos[i].x+pos[j].x)/2);
                        t.setAttribute('y', (pos[i].y+pos[j].y)/2 -3);
                        t.setAttribute('text-anchor','middle'); t.setAttribute('font-size','10'); t.setAttribute('fill','#666');
                        t.textContent = w; svg.appendChild(t);
                    }
                }
            }
        }

        // 顶点
        for (let i = 0; i < v; i++) {
            const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            c.setAttribute('cx', pos[i].x); c.setAttribute('cy', pos[i].y); c.setAttribute('r', '16');

            if (algoId === 'graph_coloring' && coloring[i] >= 0) {
                c.setAttribute('fill', graphColors[coloring[i]] || '#999');
            } else if (current === i) {
                c.setAttribute('fill', '#FF9800');
            } else if (visited[i]) {
                c.setAttribute('fill', '#4CAF50');
            } else {
                c.setAttribute('fill', '#90CAF9');
            }
            if (current === i) c.setAttribute('stroke', '#000');
            c.setAttribute('stroke-width', current === i ? '3' : '1.5');
            svg.appendChild(c);

            const lbl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            lbl.setAttribute('x', pos[i].x); lbl.setAttribute('y', pos[i].y + 5);
            lbl.setAttribute('text-anchor','middle'); lbl.setAttribute('font-size','11');
            lbl.setAttribute('font-weight','bold'); lbl.setAttribute('fill','white');
            lbl.textContent = i; svg.appendChild(lbl);
        }
    },

    /** 树对比渲染 */
    renderCompareTree(container, step) {
        const snap = step.data_snapshot;
        if (!snap) { container.innerHTML = '<p>等待树数据...</p>'; return; }
        const merged = snap.merged_history || [];
        const selected = snap.selected || [];

        if (merged.length === 0) {
            container.innerHTML = `<p style="padding:20px;"><strong>${step.description}</strong></p>`;
            return;
        }

        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%'); svg.setAttribute('height', '260');
        container.appendChild(svg);

        // 重建合并树并绘制
        const last = merged[merged.length - 1];
        const root = { id: last.parent_id, char: last.parent_char, freq: last.parent_freq, left: null, right: null };
        const map = { [root.id]: root };
        for (const m of merged) {
            map[m.parent_id] = map[m.parent_id] || { id: m.parent_id, char: m.parent_char, freq: m.parent_freq, left: null, right: null };
            map[m.left_id] = map[m.left_id] || { id: m.left_id, char: m.left_char, freq: m.left_freq, left: null, right: null };
            map[m.right_id] = map[m.right_id] || { id: m.right_id, char: m.right_char, freq: m.right_freq, left: null, right: null };
            map[m.parent_id].left = map[m.left_id];
            map[m.parent_id].right = map[m.right_id];
        }
        this.drawMiniTree(svg, root, 150, 25, 100, 55, selected);
    },

    drawMiniTree(svg, node, x, y, spread, dy, selected) {
        if (!node) return;
        const colors = ['#4A90D9','#7B68EE','#FF6B6B','#4ECDC4','#FFD93D','#6BCB77','#FF8C42','#A66CFF'];

        const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        c.setAttribute('cx', x); c.setAttribute('cy', y); c.setAttribute('r', '16');
        c.setAttribute('fill', selected.includes(node.id) ? '#FF9800' : colors[node.id % colors.length]);
        c.setAttribute('stroke', '#fff'); c.setAttribute('stroke-width', '2');
        if (selected.includes(node.id)) c.setAttribute('stroke', '#e65100');
        svg.appendChild(c);

        const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t.setAttribute('x', x); t.setAttribute('y', y + 4);
        t.setAttribute('text-anchor','middle'); t.setAttribute('font-size','9');
        t.setAttribute('fill','white'); t.setAttribute('font-weight','bold');
        t.textContent = node.freq; svg.appendChild(t);

        if (node.left) {
            const l = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            l.setAttribute('x1', x); l.setAttribute('y1', y + 16);
            l.setAttribute('x2', x - spread); l.setAttribute('y2', y + dy - 16);
            l.setAttribute('stroke','#999'); l.setAttribute('stroke-width','1'); svg.appendChild(l);
            this.drawMiniTree(svg, node.left, x - spread, y + dy, spread / 2, dy, selected);
        }
        if (node.right) {
            const l = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            l.setAttribute('x1', x); l.setAttribute('y1', y + 16);
            l.setAttribute('x2', x + spread); l.setAttribute('y2', y + dy - 16);
            l.setAttribute('stroke','#999'); l.setAttribute('stroke-width','1'); svg.appendChild(l);
            this.drawMiniTree(svg, node.right, x + spread, y + dy, spread / 2, dy, selected);
        }
    },

    /** 汉诺塔对比渲染 */
    renderCompareHanoi(container, step) {
        const pegs = step.data_snapshot?.pegs;
        if (!pegs) { container.innerHTML = '<p>等待汉诺塔数据...</p>'; return; }
        const n = step.data_snapshot?.n || 3;
        const colors = ['#FF6B6B','#4ECDC4','#FFD93D','#A66CFF','#FF8C42','#6BCB77','#00B4D8','#F77F00'];

        const wrapper = document.createElement('div');
        wrapper.style.cssText = 'display:flex;justify-content:space-around;align-items:flex-end;height:100%;padding:10px 20px;';
        ['A','B','C'].forEach(peg => {
            const div = document.createElement('div');
            div.style.cssText = 'display:flex;flex-direction:column;align-items:center;min-width:80px;';
            const lbl = document.createElement('div');
            lbl.style.cssText = 'font-weight:600;font-size:12px;margin-bottom:4px;';
            lbl.textContent = peg;
            const rod = document.createElement('div');
            rod.style.cssText = 'width:6px;height:140px;background:linear-gradient(to right,#aaa,#ddd,#aaa);border-radius:3px;position:relative;';
            (pegs[peg] || []).forEach((disk, i) => {
                const d = document.createElement('div');
                d.style.cssText = `position:absolute;bottom:${i*20}px;left:50%;transform:translateX(-50%);height:18px;border-radius:9px;background:${colors[disk-1]||'#999'};width:${30+(disk/n)*70}px;display:flex;align-items:center;justify-content:center;font-size:9px;color:white;font-weight:600;`;
                d.textContent = disk; rod.appendChild(d);
            });
            const base = document.createElement('div');
            base.style.cssText = 'width:90px;height:4px;background:#666;border-radius:2px;margin-top:2px;';
            div.appendChild(lbl); div.appendChild(rod); div.appendChild(base);
            wrapper.appendChild(div);
        });
        container.innerHTML = '';
        container.appendChild(wrapper);
    },

    togglePlay() {
        if (this.isPlaying) { this.stopPlay(); }
        else { this.startPlay(); }
        document.getElementById('comparePlayBtn').textContent = this.isPlaying ? '暂停' : '同步播放';
    },

    startPlay() {
        if (!this.results) return; this.isPlaying = true;
        const maxLen = Math.max(this.results.algorithms[0].total_steps, this.results.algorithms[1].total_steps);
        this.playInterval = setInterval(() => {
            let moved = false;
            if (this.leftStepIndex < this.results.algorithms[0].total_steps - 1) { this.leftStepIndex++; moved = true; }
            if (this.rightStepIndex < this.results.algorithms[1].total_steps - 1) { this.rightStepIndex++; moved = true; }
            if (!moved) { this.stopPlay(); return; }
            this.renderCompare();
        }, 600);
    },

    stopPlay() {
        this.isPlaying = false;
        if (this.playInterval) { clearInterval(this.playInterval); this.playInterval = null; }
        document.getElementById('comparePlayBtn').textContent = '同步播放';
    },

    reset() {
        this.stopPlay();
        this.leftStepIndex = 0; this.rightStepIndex = 0;
        this.renderCompare();
    },
};
