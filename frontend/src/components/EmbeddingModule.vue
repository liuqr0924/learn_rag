<template>
  <section class="module-section">
    <h1>向量嵌入</h1>
    <div class="module-container">
      <div class="control-panel">
        <h3>控制面板</h3>
        <div class="form-group">
          <label>分块ID：</label>
          <input type="text" v-model="chunkId" placeholder="输入分块阶段生成的chunk_id">
        </div>
        <button class="btn btn-primary" @click="handleEmbedding" :disabled="loading">
          {{ loading ? '处理中...' : '创建嵌入' }}
        </button>
      </div>
      <div class="content-display">
        <div class="display-header">
          <h3>嵌入结果</h3>
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
            <div v-if="result" class="result-cards">
              <!-- 主要信息卡片 -->
              <div class="info-cards-grid">
                <div class="info-card">
                  <div class="info-card-icon">🆔</div>
                  <div class="info-card-content">
                    <div class="info-card-label">嵌入ID</div>
                    <div class="info-card-value code-text">{{ result.embedding_id }}</div>
                  </div>
                </div>
                <div class="info-card">
                  <div class="info-card-icon">📦</div>
                  <div class="info-card-content">
                    <div class="info-card-label">分块ID</div>
                    <div class="info-card-value code-text">{{ result.chunk_id }}</div>
                  </div>
                </div>
                <div class="info-card">
                  <div class="info-card-icon">🔢</div>
                  <div class="info-card-content">
                    <div class="info-card-label">总嵌入数</div>
                    <div class="info-card-value highlight-number">{{ result.total_embeddings || result.total_chunks }}</div>
                  </div>
                </div>
                <div class="info-card">
                  <div class="info-card-icon">📐</div>
                  <div class="info-card-content">
                    <div class="info-card-label">向量维度</div>
                    <div class="info-card-value highlight-number">{{ result.embedding_dim }}</div>
                  </div>
                </div>
              </div>

              <!-- 模型和状态信息 -->
              <div class="status-section">
                <div class="status-card">
                  <div class="status-label">使用的模型</div>
                  <div class="status-value">
                    <span class="method-badge">{{ result.model || result.embedding_model || 'text-embedding-ada-002' }}</span>
                  </div>
                </div>
                <div class="status-card">
                  <div class="status-label">状态</div>
                  <div class="status-value">
                    <span class="status-badge success">{{ result.status || 'success' }}</span>
                  </div>
                </div>
              </div>

              <!-- 嵌入向量预览 -->
              <div v-if="result.preview && result.preview.length > 0" class="detail-section">
                <h4 class="section-title">
                  <span class="section-icon">👁️</span>
                  嵌入向量预览（前{{ result.preview.length }}条）
                </h4>
                <div class="preview-cards">
                  <div v-for="(chunk, index) in result.preview" :key="index" class="preview-card">
                    <div class="preview-card-header">
                      <span class="preview-index">#{{ index + 1 }}</span>
                      <span class="preview-chunk-id">块ID: {{ chunk.chunk_id }}</span>
                      <span class="preview-dim">维度: {{ chunk.embedding_dim }}</span>
                    </div>
                    <div class="preview-card-body">
                      <div class="preview-text">{{ chunk.text }}</div>
                    </div>
                  </div>
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
                    <th>嵌入ID</th>
                    <th>分块ID</th>
                    <th>模型</th>
                    <th>维度</th>
                    <th>总嵌入数</th>
                    <th>创建时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in historyList" :key="item.embedding_id">
                    <td class="file-name-cell">{{ item.embedding_id }}</td>
                    <td>{{ item.chunk_id }}</td>
                    <td><span class="method-badge">{{ item.model || 'text-embedding-ada-002' }}</span></td>
                    <td class="text-center">{{ item.embedding_dim || 1536 }}</td>
                    <td class="text-center">{{ item.total_embeddings }}</td>
                    <td class="time-cell">{{ formatTime(item.created_at) }}</td>
                    <td class="action-cell">
                      <button class="btn-view" @click.stop="loadHistoryDetail(item.embedding_id)">查看</button>
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
import { embeddingApi } from '../services/api'

const status = inject('status')
const chunkId = ref('')
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

const handleEmbedding = async () => {
  try {
    if (!chunkId.value) {
      throw new Error('请输入chunk_id')
    }
    
    loading.value = true
    result.value = null
    
    result.value = await embeddingApi.embed(chunkId.value)
    
    status.show('向量嵌入成功！', 'success')
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

const loadHistory = async () => {
  try {
    loadingHistory.value = true
    const response = await embeddingApi.getHistory()
    historyList.value = response.history || []
  } catch (error) {
    status.show(`加载历史记录失败: ${error.message}`, 'error')
    historyList.value = []
  } finally {
    loadingHistory.value = false
  }
}

const loadHistoryDetail = async (embeddingId) => {
  try {
    const detail = await embeddingApi.getDetail(embeddingId)
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
  max-width: 100%;
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

.method-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* 当前结果优化样式 */
.result-cards {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 100%;
}

.info-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.info-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
  min-width: 0;
}

.info-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.info-card-icon {
  font-size: 2rem;
  line-height: 1;
  flex-shrink: 0;
}

.info-card-content {
  flex: 1;
  min-width: 0;
}

.info-card-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-card-value {
  font-size: 1rem;
  color: var(--text-primary);
  font-weight: 600;
  word-break: break-all;
  line-height: 1.4;
}

.info-card-value.code-text {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Courier New', monospace;
  font-size: 0.9rem;
  background: var(--bg-tertiary);
  padding: 0.75rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  word-break: break-all;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

.info-card-value.highlight-number {
  font-size: 1.5rem;
  color: var(--primary-color);
  font-weight: 700;
}

.status-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.status-card {
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.status-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.detail-section {
  margin-top: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--border-color);
}

.section-icon {
  font-size: 1.25rem;
}

.preview-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-card {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.preview-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.preview-card-header {
  background: var(--bg-secondary);
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--border-color);
}

.preview-index {
  font-weight: 700;
  color: var(--primary-color);
  font-size: 0.875rem;
}

.preview-chunk-id {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Courier New', monospace;
  font-size: 0.8rem;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.preview-dim {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-left: auto;
  font-weight: 500;
}

.preview-card-body {
  padding: 1rem;
}

.preview-text {
  color: var(--text-primary);
  line-height: 1.6;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}

.preview-text::-webkit-scrollbar {
  width: 6px;
}

.preview-text::-webkit-scrollbar-track {
  background: var(--bg-tertiary);
  border-radius: 3px;
}

.preview-text::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 3px;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .info-cards-grid {
    grid-template-columns: 1fr;
  }
  
  .status-section {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 1400px) {
  .info-cards-grid {
    gap: 1.5rem;
  }
  
  .info-card {
    padding: 1.75rem;
  }
}

</style>

