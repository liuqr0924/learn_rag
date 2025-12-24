<template>
  <section class="module-section">
    <h1>文本生成</h1>
    <div class="module-container">
      <div class="control-panel">
        <h3>控制面板</h3>
        <div class="form-group">
          <label>查询问题：</label>
          <textarea v-model="query" rows="3" placeholder="输入您的问题"></textarea>
        </div>
        <div class="form-group">
          <label>过滤ID（可选）：</label>
          <input type="text" v-model="filterId" placeholder="输入过滤阶段的filter_id">
        </div>
        <div class="form-group">
          <label>最大上下文文档数：</label>
          <input type="number" v-model.number="maxContextDocs" value="5">
        </div>
        <div class="form-group">
          <label>最大Token数：</label>
          <input type="number" v-model.number="maxTokens" value="500">
        </div>
        <button class="btn btn-primary" @click="handleGeneration" :disabled="loading">
          {{ loading ? '生成中...' : '生成文本' }}
        </button>
      </div>
      <div class="content-display">
        <div class="display-header">
          <h3>生成结果</h3>
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
                    <td>生成ID</td>
                    <td>{{ result.generation_id }}</td>
                  </tr>
                  <tr>
                    <td>查询问题</td>
                    <td class="text-preview">{{ result.query }}</td>
                  </tr>
                  <tr v-if="result.filter_id">
                    <td>过滤ID</td>
                    <td>{{ result.filter_id }}</td>
                  </tr>
                  <tr>
                    <td>状态</td>
                    <td><span class="status-badge success">{{ result.status }}</span></td>
                  </tr>
                </tbody>
              </table>
              <div v-if="result.generated_text" class="detail-section">
                <h4>生成的文本</h4>
                <div class="generated-text">
                  <pre class="result-text">{{ result.generated_text }}</pre>
                </div>
              </div>
              <div v-if="result.context_documents && result.context_documents.length > 0" class="detail-section">
                <h4>使用的上下文文档（{{ result.context_documents.length }}条）</h4>
                <div class="table-wrapper">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>序号</th>
                        <th>文档内容</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(doc, index) in result.context_documents" :key="index">
                        <td>{{ index + 1 }}</td>
                        <td class="text-preview">{{ truncateText(doc, 200) }}</td>
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
                    <th>生成ID</th>
                    <th>查询问题</th>
                    <th>过滤ID</th>
                    <th>创建时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in historyList" :key="item.generation_id">
                    <td class="file-name-cell">{{ item.generation_id }}</td>
                    <td class="text-preview">{{ truncateText(item.query, 50) }}</td>
                    <td>{{ item.filter_id || '-' }}</td>
                    <td class="time-cell">{{ formatTime(item.created_at) }}</td>
                    <td class="action-cell">
                      <button class="btn-view" @click.stop="loadHistoryDetail(item.generation_id)">查看</button>
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
import { generationApi } from '../services/api'

const status = inject('status')
const query = ref('')
const filterId = ref('')
const maxContextDocs = ref(5)
const maxTokens = ref(500)
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

const handleGeneration = async () => {
  try {
    if (!query.value) {
      throw new Error('请输入查询问题')
    }
    
    loading.value = true
    result.value = null
    
    result.value = await generationApi.generate(
      query.value,
      filterId.value || null,
      maxContextDocs.value,
      maxTokens.value
    )
    
    status.show('文本生成成功！', 'success')
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
    const response = await generationApi.getHistory()
    historyList.value = response.history || []
  } catch (error) {
    status.show(`加载历史记录失败: ${error.message}`, 'error')
    historyList.value = []
  } finally {
    loadingHistory.value = false
  }
}

const loadHistoryDetail = async (generationId) => {
  try {
    const detail = await generationApi.getDetail(generationId)
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

.generated-text {
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.result-text {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  color: var(--text-primary);
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

