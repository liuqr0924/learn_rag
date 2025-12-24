<template>
  <section class="module-section">
    <h1>向量索引</h1>
    <div class="module-container">
      <div class="control-panel">
        <h3>控制面板</h3>
        <div class="form-group">
          <label>嵌入ID：</label>
          <input type="text" v-model="embeddingId" placeholder="输入嵌入阶段生成的embedding_id">
        </div>
        <div class="form-group">
          <label>集合名称：</label>
          <input type="text" v-model="collectionName" placeholder="例如: documents_collection">
        </div>
        <button class="btn btn-primary" @click="handleIndexing" :disabled="loading">
          {{ loading ? '处理中...' : '创建索引' }}
        </button>
        <hr>
        <h4>集合管理</h4>
        <button class="btn btn-secondary" @click="listCollections" :disabled="loading">
          列出所有集合
        </button>
        <div class="form-group">
          <label>删除集合：</label>
          <input type="text" v-model="deleteCollectionName" placeholder="输入集合名称">
          <button class="btn btn-danger" @click="deleteCollection" :disabled="loading">
            删除
          </button>
        </div>
        <hr>
        <h4>相似度搜索</h4>
        <div class="form-group">
          <label>查询文本：</label>
          <textarea v-model="searchQuery" rows="3" placeholder="输入查询文本"></textarea>
        </div>
        <div class="form-group">
          <label>集合名称：</label>
          <input type="text" v-model="searchCollectionName" placeholder="例如: documents_collection">
        </div>
        <div class="form-group">
          <label>返回结果数：</label>
          <input type="number" v-model.number="nResults" value="5">
        </div>
        <button class="btn btn-primary" @click="handleSearch" :disabled="loading">
          {{ loading ? '搜索中...' : '执行搜索' }}
        </button>
      </div>
      <div class="content-display">
        <div class="display-header">
          <h3>索引和搜索结果</h3>
          <div class="tab-buttons">
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'current' }"
              @click="activeTab = 'current'"
            >
              当前结果
            </button>
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'history' }"
              @click="activeTab = 'history'; loadHistory()"
            >
              历史记录
            </button>
          </div>
        </div>
        <div class="result-display">
          <!-- 当前结果 -->
          <div v-if="activeTab === 'current'">
            <div v-if="result" class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>属性</th>
                    <th>值</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="result.index_id">
                    <td>索引ID</td>
                    <td>{{ result.index_id }}</td>
                  </tr>
                  <tr v-if="result.collection_name">
                    <td>集合名称</td>
                    <td><span class="method-badge">{{ result.collection_name }}</span></td>
                  </tr>
                  <tr v-if="result.total_documents !== undefined">
                    <td>文档数</td>
                    <td>{{ result.total_documents }}</td>
                  </tr>
                  <tr v-if="result.status">
                    <td>状态</td>
                    <td><span class="status-badge success">{{ result.status }}</span></td>
                  </tr>
                  <tr v-if="result.collections">
                    <td>集合列表</td>
                    <td>{{ result.collections.length }} 个集合</td>
                  </tr>
                  <tr v-if="result.results_count !== undefined">
                    <td>搜索结果数</td>
                    <td>{{ result.results_count }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-if="result.results && result.results.length > 0" class="detail-section">
                <h4>搜索结果</h4>
                <div class="table-wrapper">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>文档内容</th>
                        <th>距离</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, index) in result.results" :key="index">
                        <td>{{ item.id }}</td>
                        <td class="text-preview">{{ truncateText(item.document, 150) }}</td>
                        <td>{{ item.distance ? item.distance.toFixed(4) : '-' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div v-if="result.collections && result.collections.length > 0" class="detail-section">
                <h4>集合详情</h4>
                <div class="table-wrapper">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>集合名称</th>
                        <th>文档数</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(col, index) in result.collections" :key="index">
                        <td>{{ col.name }}</td>
                        <td>{{ col.count }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            <div v-else class="placeholder">
              <div class="placeholder-content">
                <div class="placeholder-icon">📋</div>
                <p>暂无结果</p>
              </div>
            </div>
          </div>
          
          <!-- 历史记录 -->
          <div v-if="activeTab === 'history'" class="table-container">
            <div v-if="loadingHistory" class="loading-state">加载中...</div>
            <div v-else-if="historyList.length === 0" class="placeholder">
              <div class="placeholder-content">
                <div class="placeholder-icon">📚</div>
                <p>暂无历史记录</p>
              </div>
            </div>
            <div v-else class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>索引ID</th>
                    <th>嵌入ID</th>
                    <th>集合名称</th>
                    <th>文档数</th>
                    <th>创建时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in historyList" :key="item.index_id">
                    <td class="file-name-cell">{{ item.index_id }}</td>
                    <td>{{ item.embedding_id }}</td>
                    <td><span class="method-badge">{{ item.collection_name }}</span></td>
                    <td class="text-center">{{ item.total_documents }}</td>
                    <td class="time-cell">{{ formatTime(item.created_at) }}</td>
                    <td class="action-cell">
                      <button class="btn-view" @click.stop="loadHistoryDetail(item.index_id)">查看</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import { indexingApi } from '../services/api'

const status = inject('status')
const searchResults = inject('searchResults')
const embeddingId = ref('')
const collectionName = ref('')
const deleteCollectionName = ref('')
const searchQuery = ref('')
const searchCollectionName = ref('')
const nResults = ref(5)
const result = ref(null)
const loading = ref(false)
const activeTab = ref('current')
const historyList = ref([])
const loadingHistory = ref(false)

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const handleIndexing = async () => {
  try {
    if (!embeddingId.value || !collectionName.value) {
      throw new Error('请输入embedding_id和集合名称')
    }
    
    loading.value = true
    result.value = null
    
    result.value = await indexingApi.index(embeddingId.value, collectionName.value)
    
    status.show('索引创建成功！', 'success')
    activeTab.value = 'current'
    if (activeTab.value === 'history') {
      loadHistory()
    }
  } catch (error) {
    status.show(`错误: ${error.message}`, 'error')
  } finally {
    loading.value = false
  }
}

const listCollections = async () => {
  try {
    loading.value = true
    result.value = null
    
    result.value = await indexingApi.listCollections()
  } catch (error) {
    status.show(`错误: ${error.message}`, 'error')
  } finally {
    loading.value = false
  }
}

const deleteCollection = async () => {
  try {
    if (!deleteCollectionName.value) {
      throw new Error('请输入集合名称')
    }
    
    loading.value = true
    result.value = null
    
    result.value = await indexingApi.deleteCollection(deleteCollectionName.value)
    
    status.show('集合删除成功！', 'success')
  } catch (error) {
    status.show(`错误: ${error.message}`, 'error')
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  try {
    if (!searchQuery.value || !searchCollectionName.value) {
      throw new Error('请输入查询文本和集合名称')
    }
    
    loading.value = true
    result.value = null
    
    result.value = await indexingApi.search(
      searchCollectionName.value,
      searchQuery.value,
      nResults.value
    )
    
    // 保存搜索结果供过滤模块使用
    searchResults.value = result.value
    
    status.show('搜索完成！', 'success')
  } catch (error) {
    status.show(`错误: ${error.message}`, 'error')
  } finally {
    loading.value = false
  }
}

const loadHistory = async () => {
  try {
    loadingHistory.value = true
    const response = await indexingApi.getHistory()
    historyList.value = response.history || []
  } catch (error) {
    status.show(`加载历史记录失败: ${error.message}`, 'error')
    historyList.value = []
  } finally {
    loadingHistory.value = false
  }
}

const loadHistoryDetail = async (indexId) => {
  try {
    const detail = await indexingApi.getDetail(indexId)
    result.value = detail
    activeTab.value = 'current'
    status.show('已加载历史记录详情', 'success')
  } catch (error) {
    status.show(`加载详情失败: ${error.message}`, 'error')
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
@import '../style.css';

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
  margin-bottom: 10px;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
  margin-top: 5px;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c0392b;
}

hr {
  border: none;
  border-top: 1px solid #dee2e6;
  margin: 20px 0;
}

.display-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.tab-buttons {
  display: flex;
  gap: 0.5rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: var(--bg-hover);
}

.tab-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.table-container {
  width: 100%;
  overflow-x: auto;
}

.table-wrapper {
  max-height: 600px;
  overflow-y: auto;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  font-size: 0.875rem;
}

.data-table thead {
  background: var(--bg-secondary);
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 2px solid var(--border-color);
  white-space: nowrap;
  min-width: 80px;
}

.data-table th:nth-child(1) {
  min-width: 150px;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  word-break: break-word;
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background: var(--bg-hover);
}

.method-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.success {
  background: #10b981;
  color: white;
}

.text-preview {
  max-width: 400px;
  word-break: break-word;
  white-space: normal;
  line-height: 1.5;
}

.text-center {
  text-align: center;
}

.time-cell {
  white-space: nowrap;
  font-size: 0.8rem;
}

.action-cell {
  white-space: nowrap;
  text-align: center;
}

.btn-view {
  padding: 0.375rem 0.75rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-view:hover {
  background: #7c3aed;
  transform: translateY(-1px);
}

.detail-section {
  margin-top: 1.5rem;
}

.detail-section h4 {
  margin-bottom: 0.75rem;
  color: var(--text-primary);
  font-size: 1rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.placeholder-icon {
  font-size: 4rem;
  opacity: 0.3;
}
</style>

