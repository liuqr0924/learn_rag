<template>
  <section class="module-section">
    <h1>文档加载</h1>
    <div class="module-container">
      <div class="control-panel">
        <h3>控制面板</h3>
        <div class="form-group">
          <label>加载方法：</label>
          <select v-model="loadingMethod">
            <option value="pymupdf">PyMuPDF</option>
            <option value="pypdf">PyPDF</option>
            <option value="unstructured">Unstructured</option>
          </select>
        </div>
        <div class="form-group">
          <label>上传文件：</label>
          <input type="file" @change="handleFileChange" accept=".pdf,.docx,.txt" id="file-input">
          <div v-if="selectedFile" class="file-info">
            <span class="file-name">📎 {{ selectedFile.name }}</span>
            <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
          </div>
        </div>
        <div class="form-group">
          <label>或输入文件路径：</label>
          <input type="text" v-model="filePath" placeholder="例如: /path/to/file.pdf">
        </div>
        <button class="btn btn-primary" @click="handleLoading" :disabled="loading">
          <span v-if="loading">⏳ 加载中...</span>
          <span v-else>🚀 加载文档</span>
        </button>
      </div>
      <div class="content-display">
        <div class="display-header">
          <h3>加载结果</h3>
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
              <!-- 基本信息表格 -->
              <table class="data-table">
                <thead>
                  <tr>
                    <th>属性</th>
                    <th>值</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>文件ID</td>
                    <td>{{ result.file_id }}</td>
                  </tr>
                  <tr>
                    <td>文件名</td>
                    <td>{{ result.file_name }}</td>
                  </tr>
                  <tr>
                    <td>加载方法</td>
                    <td><span class="method-badge">{{ result.method }}</span></td>
                  </tr>
                  <tr>
                    <td>状态</td>
                    <td><span class="status-badge success">{{ result.status }}</span></td>
                  </tr>
                  <tr v-if="result.result?.total_pages">
                    <td>总页数</td>
                    <td>{{ result.result.total_pages }}</td>
                  </tr>
                  <tr v-if="result.result?.total_chunks">
                    <td>总块数</td>
                    <td>{{ result.result.total_chunks }}</td>
                  </tr>
                </tbody>
              </table>
              
              <!-- 页面/块详情表格 -->
              <div v-if="result.result?.pages || result.result?.chunks" class="detail-section">
                <h4>{{ result.result?.pages ? '页面详情' : '块详情' }}</h4>
                <div class="table-wrapper">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th v-if="result.result?.pages">页码</th>
                        <th v-if="result.result?.chunks">类型</th>
                        <th>内容预览</th>
                        <th v-if="result.result?.pages">尺寸</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, index) in (result.result?.pages || result.result?.chunks || []).slice(0, 10)" :key="index">
                        <td v-if="result.result?.pages">{{ item.page_number }}</td>
                        <td v-if="result.result?.chunks">{{ item.type || 'unknown' }}</td>
                        <td class="text-preview">{{ truncateText(item.text || String(item), 100) }}</td>
                        <td v-if="result.result?.pages && item.metadata">
                          {{ item.metadata.width }} × {{ item.metadata.height }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div v-if="(result.result?.pages || result.result?.chunks || []).length > 10" class="table-footer">
                    显示前 10 条，共 {{ (result.result?.pages || result.result?.chunks || []).length }} 条
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="placeholder">
              <div class="placeholder-content">
                <div class="placeholder-icon">📋</div>
                <p>暂无结果</p>
                <p class="placeholder-hint">请在上方选择文件或输入文件路径后点击"加载文档"</p>
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
                    <th>文件名</th>
                    <th>加载方法</th>
                    <th>页数</th>
                    <th>块数</th>
                    <th>创建时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in historyList" :key="item.file_id">
                    <td class="file-name-cell" :title="item.file_name">📄 {{ item.file_name }}</td>
                    <td><span class="method-badge">{{ item.loading_method }}</span></td>
                    <td class="text-center">{{ item.total_pages || '-' }}</td>
                    <td class="text-center">{{ item.total_chunks || '-' }}</td>
                    <td class="time-cell">{{ formatTime(item.created_at) }}</td>
                    <td class="action-cell">
                      <button class="btn-view" @click.stop="loadHistoryDetail(item.file_id)">查看</button>
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
import { loadingApi } from '../services/api'

const status = inject('status')
const loadingMethod = ref('pymupdf')
const filePath = ref('')
const selectedFile = ref(null)
const result = ref(null)
const loading = ref(false)
const activeTab = ref('current')
const historyList = ref([])
const loadingHistory = ref(false)

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

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

const handleLoading = async () => {
  try {
    loading.value = true
    result.value = null
    
    if (selectedFile.value) {
      result.value = await loadingApi.upload(selectedFile.value, loadingMethod.value)
    } else if (filePath.value) {
      result.value = await loadingApi.load(filePath.value, loadingMethod.value)
    } else {
      throw new Error('请选择文件或输入文件路径')
    }
    
    status.show('文档加载成功！', 'success')
    activeTab.value = 'current'
    // 加载成功后刷新历史记录
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
    const response = await loadingApi.getHistory()
    historyList.value = response.history || []
  } catch (error) {
    status.show(`加载历史记录失败: ${error.message}`, 'error')
    historyList.value = []
  } finally {
    loadingHistory.value = false
  }
}

const loadHistoryDetail = async (fileId) => {
  try {
    const detail = await loadingApi.getDetail(fileId)
    result.value = detail
    activeTab.value = 'current'
    status.show('已加载历史记录详情', 'success')
  } catch (error) {
    status.show(`加载详情失败: ${error.message}`, 'error')
  }
}

// 组件挂载时加载历史记录
onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.file-info {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.file-name {
  color: var(--text-primary);
  font-weight: 500;
}

.file-size {
  color: var(--text-secondary);
  font-size: 0.8rem;
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
  min-width: 100%;
}

.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #7c3aed;
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
  min-width: 200px;
}

.data-table th:nth-child(5) {
  min-width: 180px;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  word-break: break-word;
  vertical-align: middle;
}

.data-table tbody tr {
  transition: background-color 0.2s;
}

.data-table tbody tr:hover {
  background: var(--bg-hover);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
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

.file-name-cell {
  font-weight: 500;
  color: var(--text-primary);
  max-width: 300px;
  word-break: break-all;
  white-space: normal;
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

.table-footer {
  padding: 0.75rem 1rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.875rem;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
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

.placeholder-hint {
  font-size: 0.875rem;
  color: var(--text-muted);
  text-align: center;
  max-width: 300px;
}
</style>
