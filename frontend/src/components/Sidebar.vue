<template>
  <nav class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon">📚</div>
        <h2>RAG系统</h2>
      </div>
    </div>
    <ul class="nav-menu">
      <li 
        v-for="item in menuItems" 
        :key="item.id"
        :class="['nav-item', { active: activeModule === item.id }]"
        @click="handleClick(item.id)"
      >
        <a href="#" @click.prevent>
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </a>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  activeModule: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['module-change'])

const menuItems = [
  { id: 'loading', label: '文档加载', icon: '📄' },
  { id: 'chunking', label: '文档分块', icon: '✂️' },
  { id: 'parsing', label: '文档解析', icon: '🔍' },
  { id: 'embedding', label: '向量嵌入', icon: '🧮' },
  { id: 'indexing', label: '向量索引', icon: '🗂️' },
  { id: 'filtering', label: '结果过滤', icon: '🔎' },
  { id: 'generation', label: '文本生成', icon: '✨' }
]

const handleClick = (moduleId) => {
  emit('module-change', moduleId)
}
</script>

<style scoped>
.sidebar {
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  color: white;
  padding: 0;
  position: fixed;
  height: 100vh;
  width: 280px;
  overflow-y: auto;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.sidebar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.sidebar-header {
  padding: 2rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 2rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.sidebar-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  list-style: none;
  margin: 0;
  padding: 0.5rem;
}

.nav-item {
  margin: 0.25rem 0;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.nav-item a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.nav-item:hover a {
  color: white;
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
  border-left: 4px solid #6366f1;
}

.nav-item.active a {
  color: white;
  font-weight: 600;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 0 4px 4px 0;
}

.nav-icon {
  font-size: 1.25rem;
  width: 24px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-label {
  flex: 1;
  font-size: 0.95rem;
}
</style>
