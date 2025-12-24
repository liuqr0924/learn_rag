<template>
  <section class="module-section">
    <h1>结果过滤和排序</h1>
    <div class="module-container">
      <div class="control-panel">
        <h3>控制面板</h3>
        <div class="form-group">
          <label>最小分数：</label>
          <input type="number" v-model.number="minScore" step="0.1" min="0" max="1">
        </div>
        <div class="form-group">
          <label>最大分数：</label>
          <input type="number" v-model.number="maxScore" step="0.1" min="0" max="1">
        </div>
        <div class="form-group">
          <label>排序顺序：</label>
          <select v-model="sortOrder">
            <option value="desc">降序（相似度高的在前）</option>
            <option value="asc">升序</option>
          </select>
        </div>
        <p class="hint">注意：请先在索引模块执行搜索，然后将搜索结果用于过滤</p>
        <button class="btn btn-primary" @click="handleFiltering" :disabled="loading">
          {{ loading ? '处理中...' : '过滤和排序' }}
        </button>
      </div>
      <div class="content-display">
        <div class="display-header">
          <h3>过滤结果</h3>
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
                    <td>过滤ID</td>
                    <td>{{ result.filter_id }}</td>
                  </tr>
                  <tr>
                    <td>总结果数</td>
                    <td>{{ result.total_results }}</td>
                  </tr>
                  <tr>
                    <td>过滤后数量</td>
                    <td>{{ result.filtered_count }}</td>
                  </tr>
                  <tr>
                    <td>最小分数</td>
                    <td>{{ result.min_score }}</td>
                  </tr>
                  <tr>
                    <td>最大分数</td>
                    <td>{{ result.max_score }}</td>
                  </tr>
                  <tr>
                    <td>排序顺序</td>
                    <td><span class="method-badge">{{ result.sort_order === 'desc' ? '降序' : '升序' }}</span></td>
                  </tr>
                  <tr>
                    <td>状态</td>
                    <td><span class="status-badge success">{{ result.status }}</span></td>
                  </tr>
                </tbody>
              </table>
              <div v-if="result.filtered_results && result.filtered_results.length > 0" class="detail-section">
                <h4>过滤后的结果（前10条）</h4>
                <div class="table-wrapper">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>文档内容</th>
                        <th>距离/分数</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, index) in result.filtered_results.slice(0, 10)" :key="index">
                        <td>{{ item.id }}</td>
                        <td class="text-preview">{{ truncateText(item.document, 150) }}</td>
                        <td>{{ item.distance ? item.distance.toFixed(4) : '-' }}</td>
                      </tr>
                    </tbody>
                  </table>
                  <div v-if="result.filtered_results.length > 10" class="table-footer">
                    显示前 10 条，共 {{ result.filtered_results.length }} 条
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
                    <th>过滤ID</th>
                    <th>总结果数</th>
                    <th>过滤后数量</th>
                    <th>分数范围</th>
                    <th>创建时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in historyList" :key="item.filter_id">
                    <td class="file-name-cell">{{ item.filter_id }}</td>
                    <td class="text-center">{{ item.total_results }}</td>
                    <td class="text-center">{{ item.filtered_count }}</td>
                    <td>{{ item.min_score }} - {{ item.max_score }}</td>
                    <td class="time-cell">{{ formatTime(item.created_at) }}</td>
                    <td class="action-cell">
                      <button class="btn-view" @click.stop="loadHistoryDetail(item.filter_id)">查看</button>
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
import { filteringApi } from '../services/api'

const status = inject('status')
const searchResults = inject('searchResults')
const minScore = ref(0.0)
const maxScore = ref(1.0)
const sortOrder = ref('desc')
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

const handleFiltering = async () => {
  try {
    if (!searchResults.value) {
      throw new Error('请先在索引模块执行搜索')
    }
    
    loading.value = true
    result.value = null
    
    result.value = await filteringApi.filter(
      searchResults.value,
      minScore.value,
      maxScore.value,
      sortOrder.value
    )
    
    status.show('过滤和排序成功！', 'success')
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
    const response = await filteringApi.getHistory()
    historyList.value = response.history || []
  } catch (error) {
    status.show(`加载历史记录失败: ${error.message}`, 'error')
    historyList.value = []
  } finally {
    loadingHistory.value = false
  }
}

const loadHistoryDetail = async (filterId) => {
  try {
    const detail = await filteringApi.getDetail(filterId)
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

.hint {
  color: #6c757d;
  font-size: 12px;
  margin: 10px 0;
  padding: 10px;
  background-color: #fff3cd;
  border-left: 3px solid #ffc107;
  border-radius: 4px;
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
</style>

