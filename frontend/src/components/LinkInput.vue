<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits<{
  (e: 'fetched', content: any): void
}>()

const url = ref('')
const loading = ref(false)
const error = ref('')

const handleFetch = async () => {
  if (!url.value) {
    error.value = '请输入小红书链接'
    return
  }

  // 验证链接格式（支持口令和链接）
  if (!url.value.includes('xiaohongshu.com') && !url.value.includes('xhslink.com') && !url.value.match(/[A-Za-z0-9]{20,}/)) {
    error.value = '请输入正确的小红书链接或口令'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await axios.get('/api/fetch', {
      params: { url: url.value }
    })

    if (response.data.success) {
      emit('fetched', {
        url: url.value,
        ...response.data.data
      })
    } else {
      error.value = '获取内容失败'
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || '获取内容失败，请检查链接或Cookie配置'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="input-section">
    <!-- 主标题区 -->
    <div class="hero-header">
      <span class="hero-tag">
        <span class="hero-tag-dot"></span>
        CONTENT ENGINE
      </span>
      <h1 class="hero-title">
        <span class="hero-title-line1">Recreate with</span>
        <span class="hero-title-line2">Precision.</span>
      </h1>
      <p class="hero-desc">输入小红书链接，即刻开启高质感的二次创作流程。</p>
    </div>

    <!-- 核心功能卡片 -->
    <div class="input-card">
      <label class="input-label">Xiaohongshu Link</label>

      <div class="input-wrapper">
        <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
        </svg>
        <input
          v-model="url"
          type="text"
          class="link-input"
          placeholder="Paste your Little Red Book URL here..."
          @keyup.enter="handleFetch"
        />
      </div>

      <div v-if="error" class="error-message">
        <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ error }}
      </div>

      <button
        class="fetch-btn"
        :class="{ 'fetch-btn-loading': loading }"
        :disabled="loading || !url"
        @click="handleFetch"
      >
        <svg v-if="loading" class="btn-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <circle cx="12" cy="12" r="10" stroke-dasharray="60" stroke-dashoffset="20"/>
        </svg>
        <svg v-else class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
        </svg>
        <span>{{ loading ? '获取中...' : '获取内容' }}</span>
      </button>

      <!-- 功能标签组 -->
      <div class="feature-tags">
        <div class="feature-tag">
          <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <span>自动解析</span>
        </div>
        <div class="feature-tag">
          <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <span>文案还原</span>
        </div>
        <div class="feature-tag">
          <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <span>多图导出</span>
        </div>
      </div>
    </div>

    <!-- 底部提示标签组 -->
    <div class="tip-cards">
      <div class="tip-card">
        <span class="tip-title tip-title-red">PRO TIP</span>
        <p class="tip-text">支持分享口令及长链接识别</p>
      </div>
      <div class="tip-card">
        <span class="tip-title tip-title-green">SECURITY</span>
        <p class="tip-text">仅用于个人学习与创作参考</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 20px 60px;
}

/* 主标题区 */
.hero-header {
  text-align: center;
  margin-bottom: 40px;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 16px;
}

.hero-tag-dot {
  width: 6px;
  height: 6px;
  background: var(--primary-color);
  border-radius: 50%;
}

.hero-title {
  margin: 0 0 24px;
  line-height: 1.1;
}

.hero-title-line1 {
  display: block;
  font-size: 48px;
  font-weight: 700;
  color: var(--text-primary);
}

.hero-title-line2 {
  display: block;
  font-size: 48px;
  font-weight: 700;
  color: var(--primary-color);
}

.hero-desc {
  font-size: 16px;
  font-weight: 400;
  color: var(--text-color);
  line-height: 1.5;
  margin: 0;
}

/* 核心功能卡片 */
.input-card {
  width: 100%;
  max-width: 620px;
  background: var(--bg-primary);
  border-radius: 24px;
  padding: 40px;
  box-shadow: var(--shadow-lg);
}

.input-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

/* 输入框 */
.input-wrapper {
  position: relative;
  margin-bottom: 28px;
}

.link-input {
  width: 100%;
  height: 56px;
  padding: 0 20px 0 48px;
  font-size: 16px;
  font-weight: 400;
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: none;
  border-radius: 28px;
  outline: none;
  transition: background 0.2s ease;
}

.link-input::placeholder {
  color: var(--text-muted);
}

.link-input:focus {
  background: var(--bg-tertiary, #E5E7EB);
}

.input-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--text-muted);
  pointer-events: none;
}

/* 错误消息 */
.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--error-color);
  margin-bottom: 16px;
  padding: 14px 16px;
  background: rgba(239, 68, 68, 0.08);
  border-radius: 12px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  font-size: 14px;
}

.error-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: var(--error-color);
}

/* 主按钮 */
.fetch-btn {
  width: 100%;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: var(--primary-gradient);
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  box-shadow: var(--shadow-btn);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 28px;
}

.fetch-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(230, 0, 35, 0.35);
}

.fetch-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(230, 0, 35, 0.25);
}

.fetch-btn:disabled {
  background: linear-gradient(135deg, #CCCCCC 0%, #AAAAAA 100%);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.fetch-btn-loading {
  pointer-events: none;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.btn-spinner {
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 功能标签组 */
.feature-tags {
  display: flex;
  justify-content: center;
  gap: 32px;
}

.feature-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 400;
  color: var(--text-secondary);
}

.feature-icon {
  width: 16px;
  height: 16px;
  color: var(--primary-color);
}

/* 底部提示标签组 */
.tip-cards {
  display: flex;
  justify-content: center;
  gap: 16px;
  width: 100%;
  max-width: 620px;
  margin-top: 40px;
}

.tip-card {
  flex: 1;
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 16px 20px;
}

.tip-title {
  display: block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.tip-title-red {
  color: var(--primary-color);
}

.tip-title-green {
  color: var(--success-color);
}

.tip-text {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-color);
  margin: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .input-section {
    padding: 40px 16px 40px;
  }

  .hero-title-line1,
  .hero-title-line2 {
    font-size: 32px;
  }

  .input-card {
    padding: 24px;
    border-radius: 20px;
  }

  .feature-tags {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .tip-cards {
    flex-direction: column;
    gap: 12px;
  }

  .tip-card {
    width: 100%;
  }
}
</style>
