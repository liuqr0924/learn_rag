// API基础URL
const API_BASE = 'http://localhost:8000/api';

// 存储搜索结果，供过滤模块使用
let lastSearchResults = null;

// 初始化导航
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
});

// 导航功能
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.module-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const module = this.getAttribute('data-module');
            
            // 更新导航状态
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            // 更新内容显示
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(module).classList.add('active');
        });
    });
}

// 显示状态消息
function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message');
    statusEl.textContent = message;
    statusEl.className = `status-message show ${type}`;
    
    setTimeout(() => {
        statusEl.classList.remove('show');
    }, 3000);
}

// API请求封装
async function apiRequest(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            if (data instanceof FormData) {
                options.body = data;
                delete options.headers['Content-Type'];
            } else {
                options.body = JSON.stringify(data);
            }
        }
        
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || '请求失败');
        }
        
        return result;
    } catch (error) {
        showStatus(`错误: ${error.message}`, 'error');
        throw error;
    }
}

// 文档加载
async function handleLoading() {
    const method = document.getElementById('loading-method').value;
    const fileInput = document.getElementById('loading-file-input');
    const filePath = document.getElementById('loading-file-path').value;
    const resultEl = document.getElementById('loading-result');
    
    try {
        resultEl.innerHTML = '<div class="loading"></div> 正在加载...';
        
        let result;
        if (fileInput.files && fileInput.files[0]) {
            // 文件上传
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('method', method);
            
            result = await apiRequest('/loading/upload', 'POST', formData);
        } else if (filePath) {
            // 文件路径
            result = await apiRequest('/loading/load', 'POST', {
                file_path: filePath,
                method: method
            });
        } else {
            throw new Error('请选择文件或输入文件路径');
        }
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        showStatus('文档加载成功！', 'success');
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// 文档分块
async function handleChunking() {
    const fileId = document.getElementById('chunking-file-id').value;
    const strategy = document.getElementById('chunking-strategy').value;
    const chunkSize = parseInt(document.getElementById('chunk-size').value);
    const overlap = parseInt(document.getElementById('chunk-overlap').value);
    const resultEl = document.getElementById('chunking-result');
    
    try {
        if (!fileId) {
            throw new Error('请输入file_id');
        }
        
        resultEl.innerHTML = '<div class="loading"></div> 正在分块...';
        
        const result = await apiRequest('/chunking/chunk', 'POST', {
            file_id: fileId,
            chunking_strategy: strategy,
            chunk_size: chunkSize,
            overlap: overlap
        });
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        showStatus('文档分块成功！', 'success');
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// 文档解析
async function handleParsing() {
    const fileId = document.getElementById('parsing-file-id').value;
    const parseType = document.getElementById('parsing-type').value;
    const resultEl = document.getElementById('parsing-result');
    
    try {
        if (!fileId) {
            throw new Error('请输入file_id');
        }
        
        resultEl.innerHTML = '<div class="loading"></div> 正在解析...';
        
        const result = await apiRequest('/parsing/parse', 'POST', {
            file_id: fileId,
            parse_type: parseType
        });
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        showStatus('文档解析成功！', 'success');
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// 向量嵌入
async function handleEmbedding() {
    const chunkId = document.getElementById('embedding-chunk-id').value;
    const resultEl = document.getElementById('embedding-result');
    
    try {
        if (!chunkId) {
            throw new Error('请输入chunk_id');
        }
        
        resultEl.innerHTML = '<div class="loading"></div> 正在创建嵌入向量...';
        
        const result = await apiRequest('/embedding/embed', 'POST', {
            chunk_id: chunkId
        });
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        showStatus('向量嵌入成功！', 'success');
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// 向量索引
async function handleIndexing() {
    const embeddingId = document.getElementById('indexing-embedding-id').value;
    const collectionName = document.getElementById('collection-name').value;
    const resultEl = document.getElementById('indexing-result');
    
    try {
        if (!embeddingId || !collectionName) {
            throw new Error('请输入embedding_id和集合名称');
        }
        
        resultEl.innerHTML = '<div class="loading"></div> 正在创建索引...';
        
        const result = await apiRequest('/indexing/index', 'POST', {
            embedding_id: embeddingId,
            collection_name: collectionName
        });
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        showStatus('索引创建成功！', 'success');
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// 列出所有集合
async function listCollections() {
    const resultEl = document.getElementById('indexing-result');
    
    try {
        resultEl.innerHTML = '<div class="loading"></div> 正在获取集合列表...';
        
        const result = await apiRequest('/indexing/collections', 'GET');
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// 删除集合
async function deleteCollection() {
    const collectionName = document.getElementById('delete-collection-name').value;
    const resultEl = document.getElementById('indexing-result');
    
    try {
        if (!collectionName) {
            throw new Error('请输入集合名称');
        }
        
        resultEl.innerHTML = '<div class="loading"></div> 正在删除集合...';
        
        const result = await apiRequest(`/indexing/collection/${collectionName}`, 'DELETE');
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        showStatus('集合删除成功！', 'success');
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// 相似度搜索
async function handleSearch() {
    const queryText = document.getElementById('search-query').value;
    const collectionName = document.getElementById('search-collection-name').value;
    const nResults = parseInt(document.getElementById('search-n-results').value);
    const resultEl = document.getElementById('indexing-result');
    
    try {
        if (!queryText || !collectionName) {
            throw new Error('请输入查询文本和集合名称');
        }
        
        resultEl.innerHTML = '<div class="loading"></div> 正在搜索...';
        
        const result = await apiRequest('/indexing/search', 'POST', {
            collection_name: collectionName,
            query_text: queryText,
            n_results: nResults
        });
        
        // 保存搜索结果供过滤模块使用
        lastSearchResults = result;
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        showStatus('搜索完成！', 'success');
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// 结果过滤和排序
async function handleFiltering() {
    const minScore = parseFloat(document.getElementById('min-score').value);
    const maxScore = parseFloat(document.getElementById('max-score').value);
    const sortOrder = document.getElementById('sort-order').value;
    const resultEl = document.getElementById('filtering-result');
    
    try {
        if (!lastSearchResults) {
            throw new Error('请先在索引模块执行搜索');
        }
        
        resultEl.innerHTML = '<div class="loading"></div> 正在过滤和排序...';
        
        const result = await apiRequest('/filtering/filter', 'POST', {
            search_results: lastSearchResults,
            min_score: minScore,
            max_score: maxScore,
            sort_order: sortOrder
        });
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        showStatus('过滤和排序成功！', 'success');
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// 文本生成
async function handleGeneration() {
    const query = document.getElementById('generation-query').value;
    const filterId = document.getElementById('generation-filter-id').value;
    const maxContextDocs = parseInt(document.getElementById('max-context-docs').value);
    const maxTokens = parseInt(document.getElementById('max-tokens').value);
    const resultEl = document.getElementById('generation-result');
    
    try {
        if (!query) {
            throw new Error('请输入查询问题');
        }
        
        resultEl.innerHTML = '<div class="loading"></div> 正在生成文本...';
        
        const requestData = {
            query: query,
            max_context_docs: maxContextDocs,
            max_tokens: maxTokens
        };
        
        if (filterId) {
            requestData.filter_id = filterId;
        }
        
        const result = await apiRequest('/generation/generate', 'POST', requestData);
        
        resultEl.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        showStatus('文本生成成功！', 'success');
    } catch (error) {
        resultEl.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

