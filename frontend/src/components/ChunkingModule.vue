<template>
  <section class="module-section">
    <h1>文档分块</h1>
    <div class="module-container">
      <div class="control-panel">
        <h3>控制面板</h3>
        <div class="form-group">
          <label>文件ID：</label>
          <input type="text" v-model="fileId" placeholder="输入加载阶段生成的file_id">
        </div>
        <div class="form-group">
          <label>分块策略：</label>
          <select v-model="chunkingStrategy">
            <option value="by_size">按大小分块</option>
            <option value="by_sentence">按句子分块</option>
            <option value="by_paragraph">按段落分块</option>
          </select>
        </div>
        <div class="form-group">
          <label>分块大小：</label>
          <input type="number" v-model.number="chunkSize">
        </div>
        <div class="form-group">
          <label>重叠大小：</label>
          <input type="number" v-model.number="chunkOverlap">
        </div>
        <button class="btn btn-primary" @click="handleChunking" :disabled="loading">
          {{ loading ? '处理中...' : '执行分块' }}
        </button>
      </div>
      <div class="content-display">
        <div class="display-header">
          <h3>分块结果</h3>
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
                  <tr>
                    <td>分块ID</td>
                    <td>{{ result.chunk_id }}</td>
                  </tr>
                  <tr>
                    <td>文件ID</td>
                    <td>{{ result.file_id }}</td>
                  </tr>
                  <tr>
                    <td>分块策略</td>
                    <td><span class="method-badge">{{ result.strategy }}</span></td>
                  </tr>
                  <tr>
                    <td>总块数</td>
                    <td>{{ result.total_chunks }}</td>
                  </tr>
                  <tr>
                    <td>状态</td>
                    <td><span class="status-badge success">{{ result.status }}</span></td>
                  </tr>
                </tbody>
              </table>
              <div v-if="result.chunks && result.chunks.length > 0" class="detail-section">
                <h4>分块预览（前10条）</h4>
                <div class="table-wrapper">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>块ID</th>
                        <th>内容预览</th>
                        <th>长度</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(chunk, index) in result.chunks" :key="index">
                        <td>{{ chunk.chunk_id }}</td>
                        <td class="text-preview">{{ truncateText(chunk.text, 150) }}</td>
                        <td>{{ chunk.length }}</td>
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
                    <th>分块ID</th>
                    <th>文件ID</th>
                    <th>分块策略</th>
                    <th>总块数</th>
                    <th>创建时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in historyList" :key="item.chunk_id">
                    <td class="file-name-cell">{{ item.chunk_id }}</td>
                    <td>{{ item.file_id }}</td>
                    <td><span class="method-badge">{{ item.chunking_strategy }}</span></td>
                    <td class="text-center">{{ item.total_chunks }}</td>
                    <td class="time-cell">{{ formatTime(item.created_at) }}</td>
                    <td class="action-cell">
                      <button class="btn-view" @click.stop="loadHistoryDetail(item.chunk_id)">查看</button>
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
import { chunkingApi } from '../services/api'

const status = inject('status')
const fileId = ref('')
const chunkingStrategy = ref('by_size')
const chunkSize = ref(1000)
const chunkOverlap = ref(200)
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

const handleChunking = async () => {
  try {
    if (!fileId.value) {
      throw new Error('请输入file_id')
    }
    
    loading.value = true
    result.value = null
    
    result.value = await chunkingApi.chunk(
      fileId.value,
      chunkingStrategy.value,
      chunkSize.value,
      chunkOverlap.value
    )
    
    status.show('文档分块成功！', 'success')
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
    const response = await chunkingApi.getHistory()
    historyList.value = response.history || []
  } catch (error) {
    status.show(`加载历史记录失败: ${error.message}`, 'error')
    historyList.value = []
  } finally {
    loadingHistory.value = false
  }
}

const loadHistoryDetail = async (chunkId) => {
  try {
    const detail = await chunkingApi.getDetail(chunkId)
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

