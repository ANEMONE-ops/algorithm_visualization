# 算法过程可视化系统

交互式算法学习平台，支持多种算法的过程可视化、分步执行、算法对比和 AI 问答。

## 技术栈

| 层级   | 技术                                        | 版本      |
| ------ | ------------------------------------------- | --------- |
| 语言   | Python                                      | 3.10+     |
| 框架   | FastAPI                                     | 0.104.1   |
| 数据库 | SQLite (via SQLAlchemy 2.0)                 | —         |
| 前端   | 原生 HTML/CSS/JavaScript (Vanilla JS)       | ES6       |
| AI     | 豆包大模型 (火山方舟 API)                    | —         |

## 支持的算法

| 算法                    | 分类   | 时间复杂度      | 空间复杂度 |
| ----------------------- | ------ | --------------- | ---------- |
| 冒泡排序 (Bubble Sort)   | 排序   | O(n²)           | O(1)       |
| 快速排序 (Quick Sort)    | 排序   | O(n log n)      | O(log n)   |
| Prim 最小生成树          | 图算法 | O(V²)           | O(V)       |
| 哈夫曼树                 | 树结构 | O(n log n)      | O(n)       |
| 汉诺塔                   | 递归   | O(2ⁿ)           | O(n)       |
| 图着色 (回溯法)          | 回溯   | O(m^V)          | O(V)       |

## 目录结构

```
Algorithm Visualization/
├── README.md                  # 项目说明
├── requirements.txt           # Python 依赖
├── run.py                     # 开发服务器入口
├── .gitignore
├── src/
│   └── algorithm_viz/         # Python 包
│       ├── __init__.py
│       ├── app.py             # FastAPI 应用工厂
│       ├── config.py          # 全局配置
│       ├── database.py        # 数据库连接与会话
│       ├── models.py          # ORM 数据模型
│       ├── algorithms/        # 算法引擎
│       │   ├── __init__.py    # 算法注册表
│       │   ├── base.py        # 抽象基类
│       │   ├── bubble_sort.py
│       │   ├── quick_sort.py
│       │   ├── mst.py
│       │   ├── huffman.py
│       │   ├── hanoi.py
│       │   └── graph_coloring.py
│       └── routers/           # API 路由
│           ├── __init__.py
│           ├── auth.py        # 认证 (注册/登录)
│           ├── algorithms.py  # 算法执行
│           ├── ai_chat.py     # AI 对话
│           ├── compare.py     # 算法对比
│           ├── export_log.py  # 日志导出
│           └── knowledge.py   # 知识库
├── static/                    # 前端静态资源
│   ├── index.html
│   ├── login.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js             # API 通信层
│       ├── app.js             # 主应用逻辑
│       ├── auth.js            # 登录/注册
│       ├── ai-chat.js         # AI 对话
│       ├── compare.js         # 算法对比
│       ├── controls.js        # 执行控制
│       ├── knowledge.js       # 知识库
│       └── visualization.js   # 可视化渲染
└── test/
    ├── __init__.py
    ├── conftest.py            # pytest 配置
    ├── test_algorithms.py     # 算法引擎测试
    ├── test_auth.py           # 认证测试
    └── test_api.py            # API 集成测试
```

## 快速开始

### 1. 环境准备

```bash
# Python 3.10+ 环境
python --version

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python run.py
```

服务默认运行在 `http://localhost:8001`

### 4. 访问系统

打开浏览器访问 `http://localhost:8001`，首次使用需要注册账号。

## API 文档

启动服务后访问：

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 运行测试

```bash
pytest test/ -v
```

## 编程规范

- **Python**: 遵循 PEP 8 规范，使用相对导入组织包内模块
- **类型注解**: 所有函数签名包含完整的类型提示
- **文档字符串**: 每个模块和公共函数使用中文 docstring
- **单一职责**: API 路由按功能拆分，算法引擎各自独立
- **前端**: ES6 模块模式，每个 JS 文件负责独立功能域

## 注意：记得在src/algorithms/config.py里输入你自己的豆包API信息