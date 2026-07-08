/**
 * 算法可视化系统 - 可视化渲染模块
 */

const VizRenderer = {
    currentAlgo: null,
    colors: [
        '#4A90D9', '#7B68EE', '#FF6B6B', '#4ECDC4', '#FFD93D',
        '#6BCB77', '#FF8C42', '#A66CFF', '#FF5D8F', '#00B4D8',
        '#52B788', '#F77F00', '#7400B8', '#06D6A0', '#EF476F',
    ],

    /** 隐藏所有可视化层 */
    hideAll() {
        document.getElementById('vizPlaceholder').style.display = 'none';
        document.getElementById('vizSvg').style.display = 'none';
        document.getElementById('vizArray').style.display = 'none';
        document.getElementById('vizTree').style.display = 'none';
        document.getElementById('vizGraph').style.display = 'none';
        document.getElementById('vizHanoi').style.display = 'none';
    },

    /** 根据算法类型渲染步骤 */
    render(algoId, step, allSteps, stepIndex) {
        this.currentAlgo = algoId;
        this.hideAll();

        switch (algoId) {
            case 'bubble_sort':
            case 'quick_sort':
                this.renderArray(step, allSteps, stepIndex);
                break;
            case 'mst':
                this.renderMST(step, allSteps, stepIndex);
                break;
            case 'huffman':
                this.renderHuffman(step, allSteps, stepIndex);
                break;
            case 'hanoi':
                this.renderHanoi(step, allSteps, stepIndex);
                break;
            case 'graph_coloring':
                this.renderGraphColoring(step, allSteps, stepIndex);
                break;
            default:
                this.renderGeneric(step);
        }
    },

    /** 渲染数组（冒泡排序、快速排序） */
    renderArray(step, allSteps, stepIndex) {
        const container = document.getElementById('vizArray');
        container.style.display = 'flex';
        container.innerHTML = '';

        const arr = step.data_snapshot || [];
        if (!arr.length) return;

        const maxVal = Math.max(...arr, 1);
        const highlights = step.highlights || [];
        const highlights2 = step.highlights_secondary || [];

        arr.forEach((val, idx) => {
            const bar = document.createElement('div');
            bar.className = 'array-bar';

            const heightPercent = (val / maxVal) * 85;
            bar.style.height = `${Math.max(heightPercent, 10)}%`;
            bar.style.width = `${Math.max(90 / arr.length, 30)}px`;

            // 颜色
            if (highlights.includes(idx)) {
                bar.style.background = '#FF9800';
                bar.classList.add('highlight');
            } else if (highlights2.includes(idx)) {
                bar.style.background = '#4CAF50';
                bar.classList.add('sorted');
            } else {
                bar.style.background = this.colors[idx % this.colors.length];
            }

            const valSpan = document.createElement('span');
            valSpan.className = 'array-bar-value';
            valSpan.textContent = val;
            bar.appendChild(valSpan);

            const idxSpan = document.createElement('span');
            idxSpan.className = 'array-bar-index';
            idxSpan.textContent = idx;
            bar.appendChild(idxSpan);

            container.appendChild(bar);
        });

        // 显示当前步骤的变量状态
        if (step.variable_states) {
            container.dataset.vars = JSON.stringify(step.variable_states);
        }
    },

    /** 渲染最小生成树 */
    renderMST(step, allSteps, stepIndex) {
        const container = document.getElementById('vizGraph');
        container.style.display = 'block';
        container.innerHTML = '';

        const snap = step.data_snapshot;
        if (!snap) return;

        const vertices = snap.vertices || 0;
        const mstEdges = snap.mst_edges || [];
        const visited = snap.visited || [];
        const current = snap.current;
        const candidates = snap.candidates || [];
        const adjacency = snap.adjacency || {};

        // 使用SVG渲染
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '350');
        svg.setAttribute('viewBox', '-50 -50 500 400');
        container.appendChild(svg);

        // 计算顶点位置（圆形布局）
        const cx = 180, cy = 150, r = 130;
        const positions = {};
        for (let i = 0; i < vertices; i++) {
            const angle = (2 * Math.PI * i) / vertices - Math.PI / 2;
            positions[i] = {
                x: cx + r * Math.cos(angle),
                y: cy + r * Math.sin(angle),
            };
        }

        // 绘制所有边
        for (let i = 0; i < vertices; i++) {
            const adj = adjacency[i] || [];
            for (const [j, w] of adj) {
                if (i < j) {
                    const isMST = mstEdges.some(e => (e[0] === i && e[1] === j) || (e[0] === j && e[1] === i));
                    const isCandidate = candidates.some(c => (c[0] === i && c[1] === j) || (c[0] === j && c[1] === i));

                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', positions[i].x);
                    line.setAttribute('y1', positions[i].y);
                    line.setAttribute('x2', positions[j].x);
                    line.setAttribute('y2', positions[j].y);

                    if (isMST) {
                        line.setAttribute('stroke', '#4CAF50');
                        line.setAttribute('stroke-width', '3');
                    } else if (isCandidate) {
                        line.setAttribute('stroke', '#FF9800');
                        line.setAttribute('stroke-width', '2');
                        line.setAttribute('stroke-dasharray', '6,3');
                    } else {
                        line.setAttribute('stroke', '#ccc');
                        line.setAttribute('stroke-width', '1');
                    }
                    svg.appendChild(line);

                    // 权重标签
                    const midX = (positions[i].x + positions[j].x) / 2;
                    const midY = (positions[i].y + positions[j].y) / 2;
                    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    text.setAttribute('x', midX);
                    text.setAttribute('y', midY - 5);
                    text.setAttribute('text-anchor', 'middle');
                    text.setAttribute('font-size', '12');
                    text.setAttribute('fill', '#666');
                    text.textContent = w;
                    svg.appendChild(text);
                }
            }
        }

        // 绘制顶点
        for (let i = 0; i < vertices; i++) {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', positions[i].x);
            circle.setAttribute('cy', positions[i].y);
            circle.setAttribute('r', '20');

            if (current === i) {
                circle.setAttribute('fill', '#FF9800');
                circle.setAttribute('stroke', '#e65100');
                circle.setAttribute('stroke-width', '3');
            } else if (visited[i]) {
                circle.setAttribute('fill', '#4CAF50');
                circle.setAttribute('stroke', '#2e7d32');
                circle.setAttribute('stroke-width', '2');
            } else {
                circle.setAttribute('fill', '#90CAF9');
                circle.setAttribute('stroke', '#1565c0');
                circle.setAttribute('stroke-width', '1');
            }
            svg.appendChild(circle);

            // 顶点编号
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', positions[i].x);
            label.setAttribute('y', positions[i].y + 6);
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('font-size', '14');
            label.setAttribute('font-weight', 'bold');
            label.setAttribute('fill', 'white');
            label.textContent = i;
            svg.appendChild(label);
        }

        // 图例
        const legend = document.createElement('div');
        legend.className = 'viz-legend';
        legend.style.cssText = 'position:absolute;top:8px;right:12px;font-size:11px;background:rgba(255,255,255,0.9);padding:6px 10px;border-radius:4px;';
        legend.innerHTML = `
            <div>🟢 MST边 | 🟠 候选边 | ⚪ 普通边</div>
            <div>🟢已访问 | 🔵未访问 | 🟠当前顶点</div>
        `;
        container.appendChild(legend);
    },

    /** 渲染哈夫曼树 */
    renderHuffman(step, allSteps, stepIndex) {
        const container = document.getElementById('vizTree');
        container.style.display = 'flex';
        container.innerHTML = '';

        const snap = step.data_snapshot;
        if (!snap) return;

        const mergedHistory = snap.merged_history || [];
        const selected = snap.selected || [];

        if (mergedHistory.length === 0 && (!snap.nodes || snap.nodes.length === 0)) {
            container.innerHTML = '<p>等待构建哈夫曼树...</p>';
            return;
        }

        // 使用SVG绘制树
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '350');
        container.appendChild(svg);

        // 从最终合并记录重建树结构
        if (mergedHistory.length > 0) {
            const lastMerge = mergedHistory[mergedHistory.length - 1];
            const root = {
                id: lastMerge.parent_id,
                char: lastMerge.parent_char,
                freq: lastMerge.parent_freq,
                left: null, right: null,
            };

            // 构建完整树
            const nodeMap = {};
            nodeMap[root.id] = root;

            for (const m of mergedHistory) {
                if (!nodeMap[m.parent_id]) {
                    nodeMap[m.parent_id] = { id: m.parent_id, char: m.parent_char, freq: m.parent_freq, left: null, right: null };
                }
                nodeMap[m.parent_id].left = nodeMap[m.left_id] || { id: m.left_id, char: m.left_char, freq: m.left_freq, left: null, right: null };
                nodeMap[m.parent_id].right = nodeMap[m.right_id] || { id: m.right_id, char: m.right_char, freq: m.right_freq, left: null, right: null };
                nodeMap[m.left_id] = nodeMap[m.parent_id].left;
                nodeMap[m.right_id] = nodeMap[m.parent_id].right;
            }

            this.drawTreeNode(svg, root, 250, 30, 200, 60, selected);
        }
    },

    drawTreeNode(svg, node, x, y, spread, levelHeight, selected) {
        if (!node) return;

        // 绘制当前节点
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', '22');

        if (selected.includes(node.id)) {
            circle.setAttribute('fill', '#FF9800');
            circle.setAttribute('stroke', '#e65100');
            circle.setAttribute('stroke-width', '3');
        } else {
            circle.setAttribute('fill', this.colors[node.id % this.colors.length]);
            circle.setAttribute('stroke', '#fff');
            circle.setAttribute('stroke-width', '2');
        }
        svg.appendChild(circle);

        // 节点标签
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x);
        text.setAttribute('y', y - 6);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '10');
        text.setAttribute('fill', 'white');
        text.setAttribute('font-weight', 'bold');
        text.textContent = node.char.length > 8 ? node.char.substring(0, 8) + '..' : node.char;
        svg.appendChild(text);

        const freqText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        freqText.setAttribute('x', x);
        freqText.setAttribute('y', y + 10);
        freqText.setAttribute('text-anchor', 'middle');
        freqText.setAttribute('font-size', '9');
        freqText.setAttribute('fill', 'white');
        freqText.textContent = node.freq;
        svg.appendChild(freqText);

        // 绘制连接线到子节点
        if (node.left) {
            const childX = x - spread;
            const childY = y + levelHeight;
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x); line.setAttribute('y1', y + 22);
            line.setAttribute('x2', childX); line.setAttribute('y2', childY - 22);
            line.setAttribute('stroke', '#999'); line.setAttribute('stroke-width', '1.5');
            svg.appendChild(line);

            // 边标签 "0"
            const edgeLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            edgeLabel.setAttribute('x', (x + childX) / 2 - 8);
            edgeLabel.setAttribute('y', (y + childY) / 2);
            edgeLabel.setAttribute('font-size', '11');
            edgeLabel.setAttribute('fill', '#ff5252');
            edgeLabel.setAttribute('font-weight', 'bold');
            edgeLabel.textContent = '0';
            svg.appendChild(edgeLabel);

            this.drawTreeNode(svg, node.left, childX, childY, spread / 2, levelHeight, selected);
        }

        if (node.right) {
            const childX = x + spread;
            const childY = y + levelHeight;
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x); line.setAttribute('y1', y + 22);
            line.setAttribute('x2', childX); line.setAttribute('y2', childY - 22);
            line.setAttribute('stroke', '#999'); line.setAttribute('stroke-width', '1.5');
            svg.appendChild(line);

            const edgeLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            edgeLabel.setAttribute('x', (x + childX) / 2 + 2);
            edgeLabel.setAttribute('y', (y + childY) / 2);
            edgeLabel.setAttribute('font-size', '11');
            edgeLabel.setAttribute('fill', '#2979ff');
            edgeLabel.setAttribute('font-weight', 'bold');
            edgeLabel.textContent = '1';
            svg.appendChild(edgeLabel);

            this.drawTreeNode(svg, node.right, childX, childY, spread / 2, levelHeight, selected);
        }
    },

    /** 渲染汉诺塔 */
    renderHanoi(step, allSteps, stepIndex) {
        const container = document.getElementById('vizHanoi');
        container.style.display = 'flex';
        container.innerHTML = '';

        const snap = step.data_snapshot;
        if (!snap || !snap.pegs) return;

        const pegs = snap.pegs;
        const n = snap.n || 3;
        const diskColors = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#A66CFF', '#FF8C42', '#6BCB77', '#00B4D8', '#F77F00'];

        ['A', 'B', 'C'].forEach(pegName => {
            const pegDiv = document.createElement('div');
            pegDiv.className = 'hanoi-peg';

            const label = document.createElement('div');
            label.className = 'hanoi-peg-label';
            label.textContent = `柱 ${pegName}`;
            pegDiv.appendChild(label);

            const rodContainer = document.createElement('div');
            rodContainer.style.cssText = 'position:relative;display:flex;flex-direction:column-reverse;align-items:center;';

            const rod = document.createElement('div');
            rod.className = 'hanoi-peg-rod';
            rod.style.position = 'relative';

            // 绘制盘子
            const pegDisks = pegs[pegName] || [];
            pegDisks.forEach((disk, idx) => {
                const diskDiv = document.createElement('div');
                diskDiv.className = 'hanoi-disk';
                const width = 40 + (disk / n) * 100;
                diskDiv.style.width = `${width}px`;
                diskDiv.style.background = diskColors[disk - 1] || '#999';
                diskDiv.style.bottom = `${idx * 24}px`;
                diskDiv.style.zIndex = idx;
                diskDiv.textContent = disk;
                rod.appendChild(diskDiv);
            });

            rodContainer.appendChild(rod);

            const base = document.createElement('div');
            base.className = 'hanoi-peg-base';
            rodContainer.appendChild(base);

            pegDiv.appendChild(rodContainer);
            container.appendChild(pegDiv);
        });
    },

    /** 渲染图着色 */
    renderGraphColoring(step, allSteps, stepIndex) {
        const container = document.getElementById('vizGraph');
        container.style.display = 'block';
        container.innerHTML = '';

        const snap = step.data_snapshot;
        if (!snap) return;

        const vertices = snap.vertices || 0;
        const coloring = snap.coloring || [];
        const currentV = snap.current_vertex;
        const adjacency = snap.adjacency || {};
        const colorNames = ['#F44336', '#4CAF50', '#2196F3', '#FFEB3B', '#9C27B0', '#FF9800'];

        // SVG渲染
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '350');
        svg.setAttribute('viewBox', '-50 -50 500 400');
        container.appendChild(svg);

        // 圆形布局
        const cx = 180, cy = 150, r = 130;
        const positions = {};
        for (let i = 0; i < vertices; i++) {
            const angle = (2 * Math.PI * i) / vertices - Math.PI / 2;
            positions[i] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
        }

        // 绘制边
        for (let i = 0; i < vertices; i++) {
            const adj = adjacency[i] || [];
            for (const j of adj) {
                if (i < j) {
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', positions[i].x);
                    line.setAttribute('y1', positions[i].y);
                    line.setAttribute('x2', positions[j].x);
                    line.setAttribute('y2', positions[j].y);
                    line.setAttribute('stroke', '#999');
                    line.setAttribute('stroke-width', '1.5');
                    svg.appendChild(line);
                }
            }
        }

        // 绘制顶点
        for (let i = 0; i < vertices; i++) {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', positions[i].x);
            circle.setAttribute('cy', positions[i].y);
            circle.setAttribute('r', '22');

            if (coloring[i] !== undefined && coloring[i] >= 0) {
                circle.setAttribute('fill', colorNames[coloring[i]] || '#999');
            } else {
                circle.setAttribute('fill', '#ccc');
            }

            if (currentV === i) {
                circle.setAttribute('stroke', '#000');
                circle.setAttribute('stroke-width', '4');
            } else {
                circle.setAttribute('stroke', '#fff');
                circle.setAttribute('stroke-width', '2');
            }

            svg.appendChild(circle);

            // 顶点标签
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', positions[i].x);
            label.setAttribute('y', positions[i].y + 6);
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('font-size', '14');
            label.setAttribute('font-weight', 'bold');
            label.setAttribute('fill', 'white');
            label.textContent = i;
            svg.appendChild(label);
        }

        // 图例
        const legend = document.createElement('div');
        legend.style.cssText = 'position:absolute;top:8px;right:12px;font-size:11px;background:rgba(255,255,255,0.9);padding:6px 10px;border-radius:4px;';
        legend.innerHTML = colorNames.map((c, i) =>
            `<span style="display:inline-block;width:12px;height:12px;background:${c};border-radius:50%;margin-right:4px;"></span>颜色${i}`
        ).join(' ');
        container.appendChild(legend);
    },

    /** 通用渲染 */
    renderGeneric(step) {
        const placeholder = document.getElementById('vizPlaceholder');
        placeholder.style.display = 'block';
        const desc = document.getElementById('vizPlaceholder').querySelector('p');
        if (desc) desc.textContent = step.description || '执行中...';
    },

    /** 绘制SVG箭头（用于对比视图） */
    renderCompareArray(container, step, algoId) {
        const arr = step.data_snapshot || [];
        if (!arr.length) {
            container.innerHTML = '<p>等待执行...</p>';
            return;
        }

        const maxVal = Math.max(...arr, 1);
        const highlights = step.highlights || [];
        const highlights2 = step.highlights_secondary || [];

        const wrapper = document.createElement('div');
        wrapper.style.cssText = 'display:flex;align-items:flex-end;justify-content:center;gap:6px;height:100%;padding:20px;';

        arr.forEach((val, idx) => {
            const bar = document.createElement('div');
            const heightPercent = (val / maxVal) * 80;
            bar.style.cssText = `
                height:${Math.max(heightPercent, 8)}%;
                width:40px;
                border-radius:4px 4px 0 0;
                background:${highlights.includes(idx) ? '#FF9800' : highlights2.includes(idx) ? '#4CAF50' : '#4A90D9'};
                display:flex;flex-direction:column;align-items:center;justify-content:flex-end;
                transition:all 0.3s ease;
                position:relative;
            `;

            if (highlights.includes(idx)) bar.style.boxShadow = '0 0 12px rgba(255,152,0,0.8)';

            const valSpan = document.createElement('span');
            valSpan.style.cssText = 'font-size:11px;font-weight:600;color:white;margin-bottom:2px;';
            valSpan.textContent = val;
            bar.appendChild(valSpan);

            wrapper.appendChild(bar);
        });

        container.innerHTML = '';
        container.appendChild(wrapper);
    },
};
