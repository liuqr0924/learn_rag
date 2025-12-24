<template>
  <div class="app-container">
    <!-- 左侧导航栏 -->
    <Sidebar :active-module="activeModule" @module-change="handleModuleChange" />
    
    <!-- 右侧主内容区 -->
    <main class="main-content">
      <LoadingModule v-if="activeModule === 'loading'" />
      <ChunkingModule v-if="activeModule === 'chunking'" />
      <ParsingModule v-if="activeModule === 'parsing'" />
      <EmbeddingModule v-if="activeModule === 'embedding'" />
      <IndexingModule v-if="activeModule === 'indexing'" />
      <FilteringModule v-if="activeModule === 'filtering'" />
      <GenerationModule v-if="activeModule === 'generation'" />
    </main>
    
    <!-- 状态提示 -->
    <StatusMessage :message="statusMessage" :type="statusType" />
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import Sidebar from './components/Sidebar.vue'
import LoadingModule from './components/LoadingModule.vue'
import ChunkingModule from './components/ChunkingModule.vue'
import ParsingModule from './components/ParsingModule.vue'
import EmbeddingModule from './components/EmbeddingModule.vue'
import IndexingModule from './components/IndexingModule.vue'
import FilteringModule from './components/FilteringModule.vue'
import GenerationModule from './components/GenerationModule.vue'
import StatusMessage from './components/StatusMessage.vue'

const activeModule = ref('loading')
const statusMessage = ref('')
const statusType = ref('info')

// 提供全局状态管理
provide('status', {
  show: (message, type = 'info') => {
    statusMessage.value = message
    statusType.value = type
    setTimeout(() => {
      statusMessage.value = ''
    }, 3000)
  }
})

// 存储搜索结果供过滤模块使用
const lastSearchResults = ref(null)
provide('searchResults', lastSearchResults)

const handleModuleChange = (module) => {
  activeModule.value = module
}
</script>

<style scoped>
.app-container {
  display: grid;
  grid-template-columns: 280px 1fr;
  min-height: 100vh;
}

.main-content {
  margin-left: 280px;
  padding: 2rem 3rem;
  padding-top: 0;
  background: transparent;
  min-height: 100vh;
  max-width: calc(100vw - 280px);
}
</style>
