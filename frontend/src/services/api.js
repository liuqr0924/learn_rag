// API基础URL
const API_BASE = '/api'

// API请求封装
export async function apiRequest(endpoint, method = 'GET', data = null) {
  try {
    const options = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      }
    }
    
    if (data) {
      if (data instanceof FormData) {
        options.body = data
        delete options.headers['Content-Type']
      } else {
        options.body = JSON.stringify(data)
      }
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, options)
    const result = await response.json()
    
    if (!response.ok) {
      throw new Error(result.detail || '请求失败')
    }
    
    return result
  } catch (error) {
    throw error
  }
}

// 文档加载API
export const loadingApi = {
  upload: (file, method) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('method', method)
    return apiRequest('/loading/upload', 'POST', formData)
  },
  load: (filePath, method) => {
    return apiRequest('/loading/load', 'POST', {
      file_path: filePath,
      method: method
    })
  },
  getHistory: () => {
    return apiRequest('/loading/history', 'GET')
  },
  getDetail: (fileId) => {
    return apiRequest(`/loading/history/${fileId}`, 'GET')
  }
}

// 文档分块API
export const chunkingApi = {
  chunk: (fileId, chunkingStrategy, chunkSize, overlap) => {
    return apiRequest('/chunking/chunk', 'POST', {
      file_id: fileId,
      chunking_strategy: chunkingStrategy,
      chunk_size: chunkSize,
      overlap: overlap
    })
  },
  getHistory: () => {
    return apiRequest('/chunking/history', 'GET')
  },
  getDetail: (chunkId) => {
    return apiRequest(`/chunking/history/${chunkId}`, 'GET')
  }
}

// 文档解析API
export const parsingApi = {
  parse: (fileId, parseType) => {
    return apiRequest('/parsing/parse', 'POST', {
      file_id: fileId,
      parse_type: parseType
    })
  },
  getHistory: () => {
    return apiRequest('/parsing/history', 'GET')
  },
  getDetail: (parseId) => {
    return apiRequest(`/parsing/history/${parseId}`, 'GET')
  }
}

// 向量嵌入API
export const embeddingApi = {
  embed: (chunkId) => {
    return apiRequest('/embedding/embed', 'POST', {
      chunk_id: chunkId
    })
  },
  getHistory: () => {
    return apiRequest('/embedding/history', 'GET')
  },
  getDetail: (embeddingId) => {
    return apiRequest(`/embedding/history/${embeddingId}`, 'GET')
  }
}

// 向量索引API
export const indexingApi = {
  createCollection: (collectionName, embeddingDim = 1536) => {
    return apiRequest(`/indexing/create-collection?collection_name=${collectionName}&embedding_dim=${embeddingDim}`, 'POST')
  },
  index: (embeddingId, collectionName) => {
    return apiRequest('/indexing/index', 'POST', {
      embedding_id: embeddingId,
      collection_name: collectionName
    })
  },
  search: (collectionName, queryText, nResults = 5) => {
    return apiRequest('/indexing/search', 'POST', {
      collection_name: collectionName,
      query_text: queryText,
      n_results: nResults
    })
  },
  listCollections: () => {
    return apiRequest('/indexing/collections', 'GET')
  },
  deleteCollection: (collectionName) => {
    return apiRequest(`/indexing/collection/${collectionName}`, 'DELETE')
  },
  getHistory: () => {
    return apiRequest('/indexing/history', 'GET')
  },
  getDetail: (indexId) => {
    return apiRequest(`/indexing/history/${indexId}`, 'GET')
  }
}

// 结果过滤API
export const filteringApi = {
  filter: (searchResults, minScore, maxScore, sortOrder) => {
    return apiRequest('/filtering/filter', 'POST', {
      search_results: searchResults,
      min_score: minScore,
      max_score: maxScore,
      sort_order: sortOrder
    })
  },
  getHistory: () => {
    return apiRequest('/filtering/history', 'GET')
  },
  getDetail: (filterId) => {
    return apiRequest(`/filtering/history/${filterId}`, 'GET')
  }
}

// 文本生成API
export const generationApi = {
  generate: (query, filterId, maxContextDocs, maxTokens) => {
    const data = {
      query: query,
      max_context_docs: maxContextDocs,
      max_tokens: maxTokens
    }
    if (filterId) {
      data.filter_id = filterId
    }
    return apiRequest('/generation/generate', 'POST', data)
  },
  getHistory: () => {
    return apiRequest('/generation/history', 'GET')
  },
  getDetail: (generationId) => {
    return apiRequest(`/generation/history/${generationId}`, 'GET')
  }
}

