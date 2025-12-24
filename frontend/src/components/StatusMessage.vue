<template>
  <Transition name="slide-up">
    <div v-if="message" :class="['status-message', 'show', type]">
      <span class="status-icon">{{ getIcon() }}</span>
      <span class="status-text">{{ message }}</span>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'info'
  }
})

const getIcon = () => {
  const icons = {
    success: '✅',
    error: '❌',
    info: 'ℹ️',
    warning: '⚠️'
  }
  return icons[props.type] || icons.info
}
</script>

<style scoped>
.status-message {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: var(--shadow-xl);
  display: none;
  z-index: 2000;
  max-width: 400px;
  backdrop-filter: blur(10px);
  animation: slideIn 0.3s ease-out;
}

.status-message.show {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-icon {
  font-size: 1.25rem;
}

.status-text {
  flex: 1;
  font-weight: 500;
}

.status-message.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.status-message.error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.status-message.info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.status-message.warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
