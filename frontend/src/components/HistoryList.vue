<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface HistoryItem {
  task_id: string
  url: string
  original_title: string
  generated_title: string | null
  status: string
  created_at: string
  completed_at: string | null
}

const history = ref<HistoryItem[]>([])
const loading = ref(false)
const expanded = ref(false)

const statusText: Record<string, string> = {
  pending: '等待中',
  fetching: '获取中',
  analyzing: '分析中',
  generating: '生成中',
  writing: '写作中',
  completed: '已完成',
  failed: '失败',
}

const fetchHistory = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/history', {
      params: { page: 1, page_size: 10 },
    })
    history.value = response.data.items
  } catch (e) {
    console.error('Failed to fetch history:', e)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="card history-card">
    <div class="history-header" @click="expanded = !expanded">
      <h2 class="card-title">历史记录</h2>
      <span class="toggle">{{ expanded ? '收起' : '展开' }}</span>
    </div>

    <div v-if="expanded" class="history-content">
      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="history.length === 0" class="empty">
        暂无历史记录
      </div>

      <div v-else class="history-list">
        <div
          v-for="item in history"
          :key="item.task_id"
          class="history-item"
        >
          <div class="history-info">
            <p class="history-title">{{ item.original_title || '无标题' }}</p>
            <p class="history-url">{{ item.url }}</p>
          </div>
          <div class="history-meta">
            <span class="status-badge" :class="`status-${item.status}`">
              {{ statusText[item.status] || item.status }}
            </span>
            <span class="history-time">{{ formatDate(item.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-card {
  margin-top: 20px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
  padding: 4px 0;
  transition: opacity 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.history-header:hover {
  opacity: 0.8;
}

.history-header:active {
  opacity: 0.6;
}

.history-header .card-title {
  margin: 0;
}

.toggle {
  color: var(--primary-color);
  font-size: 14px;
  font-weight: 500;
  padding: 6px 12px;
  background: rgba(244, 63, 94, 0.08);
  border-radius: 6px;
  transition: all 0.2s;
}

.history-header:hover .toggle {
  background: rgba(244, 63, 94, 0.15);
}

.history-content {
  margin-top: 16px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 14px 16px;
  background: var(--bg-secondary);
  border-radius: 10px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: rgba(244, 63, 94, 0.2);
  background: rgba(244, 63, 94, 0.03);
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-title {
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}

.history-url {
  font-size: 12px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
  margin-left: 12px;
}

.history-time {
  font-size: 11px;
  color: var(--text-secondary);
}

.loading,
.empty {
  text-align: center;
  padding: 24px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border-radius: 10px;
}
</style>
