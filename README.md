# RAG Practical Camp - 检索增强生成系统

这是一个完整的**RAG（检索增强生成）系统**，实现了从文档处理到智能问答的全流程功能。系统采用模块化设计，支持多种文档处理策略和向量嵌入方案，适用于知识库构建、文档检索和智能问答等场景。

## ✨ 核心特性

- 📄 **多格式文档支持**: PDF、DOCX、TXT等多种文档格式
- 🔧 **灵活的文档处理**: 支持多种加载、分块和解析策略
- 🧮 **本地/云端嵌入**: 支持本地sentence-transformers模型和Azure OpenAI
- 🔍 **高效向量检索**: 基于ChromaDB的相似度搜索
- 🎯 **智能结果过滤**: 可选的相似度过滤和排序功能
- 💬 **上下文增强生成**: 基于检索结果生成准确回答
- 🎨 **现代化UI**: Vue 3 + Vite构建的响应式前端界面

## 📋 功能模块

系统包含7个核心功能模块，按照RAG流程顺序组织：

1. **📥 文档加载 (Loading)**: 支持PyMuPDF、PyPDF和Unstructured三种文档加载方式
2. **✂️ 文档分块 (Chunking)**: 支持按大小、按句子、按段落等多种分块策略
3. **🔍 文档解析 (Parsing)**: 支持全文、分页、按标题、混合（表格+文本）解析
4. **🧮 向量嵌入 (Embedding)**: 支持本地sentence-transformers模型（默认）和Azure OpenAI
5. **📁 向量索引 (Indexing)**: 使用ChromaDB存储和检索向量，支持相似度搜索
6. **🔎 结果过滤 (Filtering)**: 对搜索结果进行相似度过滤和排序（可选模块）
7. **✨ 文本生成 (Generation)**: 使用Azure OpenAI基于上下文生成文本回答

## 🛠️ 技术栈

### 后端
- **FastAPI**: 现代、快速的Web框架
- **sentence-transformers**: 本地向量嵌入模型（默认：bert-base-uncased）
- **Azure OpenAI**: 文本生成和可选的向量嵌入
- **ChromaDB**: 轻量级向量数据库
- **PyMuPDF/PyPDF/Unstructured**: 多格式文档处理库
- **LangChain**: 文档处理工具链

### 前端
- **Vue 3**: 渐进式JavaScript框架
- **Vite**: 快速的前端构建工具
- **组件化设计**: 模块化的Vue组件
- **响应式布局**: 左侧导航栏 + 右侧内容显示

## 🚀 快速开始

### 前置要求

- **Python**: 3.8+
- **Node.js**: 16.0+
- **pip** 和 **npm**

### 1. 安装后端依赖

```bash
pip install -r backend/requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 配置环境变量（可选）

系统默认使用**本地embedding模型**，无需配置即可使用。如果需要使用Azure OpenAI进行文本生成，请在 `backend` 目录下创建 `.env` 文件：

```bash
cd backend
# 创建.env文件
```

编辑 `backend/.env` 文件：

```env
# 本地embedding配置（默认）
USE_LOCAL_EMBEDDING=true
LOCAL_EMBEDDING_MODEL=bert-base-uncased

# Azure OpenAI配置（用于文本生成，可选）
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=
AZURE_OPENAI_CHAT_DEPLOYMENT=
```

**注意**：
- 如果只使用本地embedding模型，可以省略Azure OpenAI配置
- 文本生成模块需要Azure OpenAI配置
- 首次使用本地模型会自动从Hugging Face下载（可能需要VPN）

### 4. 启动服务

#### 方式一：开发模式（推荐）

**终端1 - 启动后端**：
```bash
# 在项目根目录
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**终端2 - 启动前端**：
```bash
cd frontend
npm run dev
```

访问地址：
- 前端开发服务器：`http://localhost:3000`（或Vite默认端口）
- 后端API文档：`http://localhost:8000/docs`

#### 方式二：生产模式

```bash
# 1. 构建前端
cd frontend
npm run build

# 2. 启动后端（会自动服务前端静态文件）
cd ..
python backend/main.py
```

访问地址：`http://localhost:8000`

## 📖 使用流程

系统按照RAG标准流程工作，各模块通过ID传递数据：

### 文档处理阶段（离线）

```
1. 文档加载
   ├─ 上传文件或指定路径
   ├─ 选择加载方法（PyMuPDF/PyPDF/Unstructured）
   └─ 输出：file_id

2. 文档分块（必需）
   ├─ 使用 file_id
   ├─ 选择分块策略（按大小/按句子/按段落）
   └─ 输出：chunk_id

3. 文档解析（可选，与分块并行）
   ├─ 使用 file_id
   ├─ 选择解析类型（全文/分页/按标题/混合）
   └─ 输出：parse_id

4. 向量嵌入
   ├─ 使用 chunk_id
   ├─ 使用本地embedding模型（默认）或Azure OpenAI
   └─ 输出：embedding_id

5. 向量索引
   ├─ 使用 embedding_id
   ├─ 指定集合名称（collection_name）
   ├─ 存储到ChromaDB
   └─ 输出：index_id
```

### 查询阶段（在线）

```
1. 用户输入查询
   ↓
2. 向量索引搜索
   ├─ 将查询转换为向量
   ├─ 在ChromaDB中搜索相似文档
   └─ 输出：搜索结果列表（包含距离分数）
   ↓
3. 结果过滤（可选）
   ├─ 按相似度分数过滤（min_score/max_score）
   ├─ 排序（降序/升序）
   └─ 输出：filter_id, 过滤后的结果
   ↓
4. 文本生成
   ├─ 使用用户查询 + 上下文文档（过滤后的结果）
   ├─ 调用Azure OpenAI GPT API
   └─ 输出：最终回答
```

### 关键说明

- **ID传递机制**: 每个模块的输出ID作为下一个模块的输入
  - `file_id` → `chunk_id` → `embedding_id` → `index_id` → `filter_id`
- **可选模块**: 
  - 文档解析可以独立进行，不依赖分块
  - 结果过滤是可选的，可以直接使用搜索结果进行生成
- **数据持久化**: 所有处理结果保存在 `backend/data/` 目录下，便于追溯和复用

## 📁 项目结构

```
RAG Practical Camp/
├── backend/                    # 后端服务
│   ├── main.py                 # FastAPI应用入口
│   ├── requirements.txt        # Python依赖
│   ├── .env                    # 环境变量配置（需自行创建）
│   ├── routers/                # API路由模块
│   │   ├── loading.py          # 文档加载路由
│   │   ├── chunking.py         # 文档分块路由
│   │   ├── parsing.py          # 文档解析路由
│   │   ├── embedding.py        # 向量嵌入路由
│   │   ├── indexing.py         # 向量索引路由
│   │   ├── filtering.py        # 结果过滤路由
│   │   └── generation.py       # 文本生成路由
│   ├── services/               # 业务逻辑服务层
│   │   ├── loading_service.py
│   │   ├── chunking_service.py
│   │   ├── parsing_service.py
│   │   ├── embedding_service.py
│   │   ├── indexing_service.py
│   │   ├── filtering_service.py
│   │   └── generation_service.py
│   ├── utils/                  # 工具函数
│   │   ├── config.py           # 配置管理
│   │   └── storage.py          # 数据存储
│   ├── data/                   # 处理结果存储（自动创建）
│   │   ├── loading/            # 文档加载结果
│   │   ├── chunking/           # 分块结果
│   │   ├── parsing/            # 解析结果
│   │   ├── embedding/          # 嵌入结果
│   │   ├── indexing/           # 索引结果
│   │   ├── filtering/          # 过滤结果
│   │   ├── generation/         # 生成结果
│   │   └── upload/             # 上传文件
│   ├── chroma_db/              # ChromaDB向量数据库（自动创建）
│   └── INSTALL_LOCAL_EMBEDDING.md  # 本地模型安装指南
├── frontend/                   # 前端应用
│   ├── index.html              # 入口HTML
│   ├── package.json            # npm配置
│   ├── vite.config.js          # Vite配置
│   ├── src/
│   │   ├── main.js             # Vue应用入口
│   │   ├── App.vue             # 根组件
│   │   ├── style.css           # 全局样式
│   │   ├── components/         # Vue组件
│   │   │   ├── Sidebar.vue     # 侧边栏导航
│   │   │   ├── LoadingModule.vue
│   │   │   ├── ChunkingModule.vue
│   │   │   ├── ParsingModule.vue
│   │   │   ├── EmbeddingModule.vue
│   │   │   ├── IndexingModule.vue
│   │   │   ├── FilteringModule.vue
│   │   │   ├── GenerationModule.vue
│   │   │   └── StatusMessage.vue
│   │   └── services/           # API服务
│   │       └── api.js          # API调用封装
│   └── dist/                   # 构建输出（npm run build后生成）
├── notebooks/                  # Jupyter笔记本
│   └── RAG系统完整流程演示.ipynb
├── RAG系统功能模块关系说明.md   # 详细功能说明文档
├── 启动指南.md                 # 启动指南
└── README.md                   # 项目说明文档
```

## 📚 详细文档

- **[RAG系统功能模块关系说明.md](temp/RAG系统功能模块关系说明.md)**: 详细的模块功能说明和工作流程
- **[启动指南.md](temp/启动指南.md)**: 详细的启动步骤说明
- **[backend/INSTALL_LOCAL_EMBEDDING.md](temp/INSTALL_LOCAL_EMBEDDING.md)**: 本地embedding模型安装和配置指南

## 🔧 API文档

启动后端服务后，访问以下地址查看API文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 💡 使用示例

### 完整RAG流程示例

1. **上传文档** → 在"文档加载"模块上传PDF文件，获得 `file_id`
2. **文档分块** → 使用 `file_id` 进行分块，获得 `chunk_id`
3. **向量嵌入** → 使用 `chunk_id` 创建嵌入向量，获得 `embedding_id`
4. **创建索引** → 使用 `embedding_id` 创建索引到ChromaDB，获得 `index_id`
5. **执行搜索** → 在索引模块输入查询文本，搜索相关文档
6. **过滤结果**（可选）→ 对搜索结果进行相似度过滤
7. **生成回答** → 使用查询和上下文生成最终回答

### 本地Embedding模型使用

系统默认使用本地embedding模型（`bert-base-uncased`），无需配置即可使用：

- ✅ **优点**: 无需网络连接，无需API密钥，数据隐私更好
- ⚠️ **注意**: 首次使用会自动下载模型（约400MB），需要网络连接
- 🔄 **切换模型**: 在 `.env` 中修改 `LOCAL_EMBEDDING_MODEL` 参数

## ⚠️ 注意事项

1. **数据存储**: 
   - 所有处理结果保存在 `backend/data/` 目录下的JSON文件中
   - 向量数据存储在 `backend/chroma_db/` 目录中
   - 上传的文件保存在 `backend/data/loading/upload/` 目录

2. **环境配置**:
   - 本地embedding模型默认启用，无需配置
   - 文本生成功能需要Azure OpenAI配置
   - 首次使用本地模型需要下载（可能需要VPN）

3. **前端部署**:
   - 开发模式：使用 `npm run dev`，访问Vite开发服务器
   - 生产模式：先执行 `npm run build`，然后启动后端服务

4. **版本要求**:
   - Python >= 3.8
   - Node.js >= 16.0.0

5. **性能优化**:
   - 本地embedding模型在CPU上运行，处理大量文档时可能较慢
   - 建议使用GPU加速（需要安装PyTorch GPU版本）
   - 可以切换到Azure OpenAI以获得更好的性能

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

