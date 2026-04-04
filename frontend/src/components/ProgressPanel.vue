<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { api } from '../utils/auth'

const props = defineProps<{
  taskId: string
}>()

const emit = defineEmits<{
  (e: 'complete', result: any): void
  (e: 'reset'): void
}>()

const status = ref('pending')
const progress = ref(0)
const message = ref('准备开始...')
const currentStep = ref('')

let ws: WebSocket | null = null
let pingInterval: number | null = null

const statusText: Record<string, string> = {
  pending: '等待中',
  fetching: '获取内容中',
  analyzing: '分析图片中',
  generating: '生成图片中',
  writing: '生成文案中',
  completed: '已完成',
  failed: '失败',
}

// 步骤定义
const steps = computed(() => [
  {
    name: '解析链接',
    status: getStepStatus('fetching'),
    done: ['fetching', 'analyzing', 'generating', 'writing', 'completed'].includes(status.value)
  },
  {
    name: '分析图片',
    status: getStepStatus('analyzing'),
    done: ['analyzing', 'generating', 'writing', 'completed'].includes(status.value)
  },
  {
    name: '生成内容',
    status: getStepStatus('generating'),
    done: ['writing', 'completed'].includes(status.value)
  }
])

function getStepStatus(stepName: string): string {
  const order = ['pending', 'fetching', 'analyzing', 'generating', 'writing', 'completed']
  const currentIndex = order.indexOf(status.value)
  const stepIndex = order.indexOf(stepName)

  if (stepIndex < currentIndex) return 'done'
  if (stepIndex === currentIndex) return 'progress'
  return 'queued'
}

// 获取完整任务结果
const fetchTaskResult = async () => {
  try {
    const response = await api.get(`/api/task/${props.taskId}`)
    return response.data
  } catch (e) {
    console.error('Failed to fetch task result:', e)
    return null
  }
}

const connectWebSocket = () => {
  const wsUrl = `ws://${window.location.host}/ws/${props.taskId}`
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('WebSocket connected')
    // 心跳
    pingInterval = window.setInterval(() => {
      ws?.send('ping')
    }, 30000)
  }

  ws.onmessage = async (event) => {
    try {
      const data = JSON.parse(event.data)

      // 忽略心跳响应消息
      if (data.type === 'pong') {
        return
      }

      status.value = data.status
      progress.value = data.progress
      message.value = data.message || statusText[data.status] || ''
      currentStep.value = data.current_step || ''

      if (data.status === 'completed') {
        // 获取完整结果
        const result = await fetchTaskResult()
        emit('complete', result || data)
      }
    } catch (e) {
      console.error('Failed to parse message:', e)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  ws.onclose = () => {
    console.log('WebSocket closed')
    if (pingInterval) {
      clearInterval(pingInterval)
    }
  }
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
  if (pingInterval) {
    clearInterval(pingInterval)
  }
})
</script>

<template>
  <div class="progress-section">
    <!-- 页面流程步骤引导 -->
    <div class="page-step-indicator">
      <div class="page-step-item completed">
        <span class="page-step-number">1</span>
        <span class="page-step-label">链接导入</span>
      </div>
      <div class="page-step-line completed"></div>
      <div class="page-step-item completed">
        <span class="page-step-number">2</span>
        <span class="page-step-label">内容解析</span>
      </div>
      <div class="page-step-line completed"></div>
      <div class="page-step-item active">
        <span class="page-step-number">3</span>
        <span class="page-step-label">重塑创作</span>
      </div>
      <div class="page-step-line"></div>
      <div class="page-step-item">
        <span class="page-step-number">4</span>
        <span class="page-step-label">成果展示</span>
      </div>
    </div>

    <!-- 顶部状态图标区 -->
    <div class="status-icon-wrapper">
      <div class="status-icon">
        <svg class="sparkle sparkle-main" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"/>
        </svg>
        <svg class="sparkle sparkle-small sparkle-1" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"/>
        </svg>
        <svg class="sparkle sparkle-small sparkle-2" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"/>
        </svg>
      </div>
    </div>

    <!-- 状态文本区 -->
    <div class="status-text-area">
      <span class="status-tag">处理中</span>
      <h1 class="status-title">正在为您二创中…</h1>
      <p class="status-desc">我们正在对您的内容进行智能分析和创意重构，请稍候片刻。</p>
    </div>

    <!-- 核心进度步骤卡片 -->
    <div class="progress-card">
      <!-- 进度条 + 百分比 -->
      <div class="progress-header-row">
        <div class="progress-bar">
          <div class="progress-bar-fill" :style="{ width: `${progress}%` }"></div>
        </div>
        <span class="progress-percent">{{ progress }}%</span>
      </div>

      <!-- 动态消息 -->
      <div class="progress-message" v-if="message">
        <span>{{ message }}</span>
      </div>

      <!-- 步骤列表 -->
      <div class="steps-list">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="step-item"
          :class="{ 'step-done': step.status === 'done', 'step-progress': step.status === 'progress', 'step-queued': step.status === 'queued' }"
        >
          <div class="step-left">
            <div class="step-icon">
              <!-- 已完成 -->
              <svg v-if="step.status === 'done'" class="icon-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <!-- 进行中 -->
              <div v-else-if="step.status === 'progress'" class="icon-progress-inner"></div>
            </div>
            <span class="step-name">{{ step.name }}</span>
          </div>
          <span class="step-status">
            {{ step.status === 'done' ? '完成' : step.status === 'progress' ? '进行中' : '等待中' }}
          </span>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-if="status === 'failed'" class="error-section">
      <p>处理失败，请重试</p>
      <button class="btn btn-primary" @click="emit('reset')">
        重新开始
      </button>
    </div>
  </div>
</template>

<style scoped>
.progress-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 20px;
}

/* 页面流程步骤引导 */
.page-step-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 40px;
  width: 100%;
}

.page-step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.4;
}

.page-step-item.active {
  opacity: 1;
}

.page-step-item.completed {
  opacity: 1;
}

.page-step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-secondary);
}

.page-step-item.active .page-step-number {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.page-step-item.completed .page-step-number {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.page-step-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.page-step-item.active .page-step-label {
  color: var(--text-primary);
}

.page-step-line {
  width: 32px;
  height: 1px;
  background: var(--border-color);
  opacity: 0.3;
}

.page-step-line.completed {
  background: var(--primary-color);
  opacity: 0.5;
}

/* 顶部状态图标区 */
.status-icon-wrapper {
  margin-bottom: 32px;
}

.status-icon {
  width: 120px;
  height: 120px;
  background: var(--bg-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: var(--shadow-lg);
}

.sparkle {
  color: var(--primary-color);
  opacity: 0.6;
}

.sparkle-main {
  width: 48px;
  height: 48px;
}

.sparkle-small {
  width: 24px;
  height: 24px;
  position: absolute;
}

.sparkle-1 {
  top: 24px;
  right: 20px;
}

.sparkle-2 {
  bottom: 28px;
  left: 24px;
}

/* 状态文本区 */
.status-text-area {
  text-align: center;
  margin-bottom: 32px;
}

.status-tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-color);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.status-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  margin: 0 0 16px;
}

.status-desc {
  font-size: 16px;
  font-weight: 400;
  color: var(--text-color);
  line-height: 1.5;
  margin: 0;
  max-width: 480px;
}

/* 核心进度步骤卡片 */
.progress-card {
  width: 100%;
  max-width: 600px;
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 32px;
}

/* 进度条 */
.progress-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
}

.progress-percent {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
  min-width: 40px;
  text-align: right;
}

.progress-bar-fill {
  height: 100%;
  background: var(--primary-gradient);
  border-radius: 3px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 动态消息 */
.progress-message {
  text-align: center;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: rgba(230, 0, 35, 0.05);
  border-radius: 8px;
}

.progress-message span {
  font-size: 14px;
  font-weight: 500;
  color: var(--primary-color);
}

/* 步骤列表 */
.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
}

.step-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* 已完成状态 */
.step-done .step-icon {
  background: var(--success-color);
}

.step-done .icon-check {
  width: 12px;
  height: 12px;
  color: white;
}

.step-done .step-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.step-done .step-status {
  font-size: 14px;
  font-weight: 600;
  color: var(--success-color);
}

/* 进行中状态 */
.step-progress .step-icon {
  border: 2px solid var(--primary-color);
  background: transparent;
}

.step-progress .icon-progress-inner {
  width: 8px;
  height: 8px;
  background: var(--primary-color);
  opacity: 0.6;
  border-radius: 50%;
}

.step-progress .step-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.step-progress .step-status {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
}

/* 等待中状态 */
.step-queued .step-icon {
  border: 2px solid var(--border-color);
  background: transparent;
}

.step-queued .step-name {
  font-size: 16px;
  font-weight: 400;
  color: var(--text-muted);
}

.step-queued .step-status {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
}

/* 错误状态 */
.error-section {
  margin-top: 24px;
  text-align: center;
  padding: 24px;
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
}

.error-section p {
  color: var(--error-color);
  margin-bottom: 16px;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 768px) {
  .status-title {
    font-size: 28px;
  }

  .status-icon {
    width: 100px;
    height: 100px;
  }

  .sparkle-main {
    width: 40px;
    height: 40px;
  }

  .sparkle-small {
    width: 20px;
    height: 20px;
  }

  .progress-card {
    padding: 24px;
  }
}
</style>
