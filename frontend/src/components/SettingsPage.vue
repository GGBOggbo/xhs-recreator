<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { authApi } from '../utils/auth'

const emit = defineEmits<{
  (e: 'go-back'): void
}>()

const cookieText = ref('')
const cookieStatus = ref<'none' | 'saved' | 'valid' | 'invalid'>('none')
const saving = ref(false)
const checking = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

onMounted(async () => {
  try {
    const res = await authApi.getCookieStatus()
    if (res.data?.data?.has_cookie) {
      cookieStatus.value = 'saved'
    }
  } catch {}
})

const handleSave = async () => {
  if (saving.value) return
  if (!cookieText.value.trim()) {
    message.value = '请先粘贴 Cookie 内容'
    messageType.value = 'error'
    return
  }

  saving.value = true
  message.value = ''

  try {
    await authApi.saveCookie({ cookies: cookieText.value.trim() })
    cookieStatus.value = 'saved'
    message.value = 'Cookie 保存成功'
    messageType.value = 'success'
    cookieText.value = ''
  } catch (e: any) {
    message.value = e.response?.data?.detail || '保存失败，请重试'
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
}

const handleCheck = async () => {
  if (checking.value) return
  if (cookieStatus.value === 'none') {
    message.value = '请先保存 Cookie'
    messageType.value = 'error'
    return
  }

  checking.value = true
  message.value = ''

  try {
    const res = await authApi.checkCookie()
    const valid = res.data?.data?.valid
    cookieStatus.value = valid ? 'valid' : 'invalid'
    message.value = valid ? 'Cookie 有效' : 'Cookie 已失效，请重新获取'
    messageType.value = valid ? 'success' : 'error'
  } catch (e: any) {
    cookieStatus.value = 'invalid'
    message.value = e.response?.data?.detail || '检测失败，请重试'
    messageType.value = 'error'
  } finally {
    checking.value = false
  }
}

const statusLabel: Record<string, string> = {
  none: '未配置',
  saved: '已配置（未检测）',
  valid: '已配置（有效）',
  invalid: '已配置（已过期）',
}

const statusClass: Record<string, string> = {
  none: 'status-none',
  saved: 'status-saved',
  valid: 'status-valid',
  invalid: 'status-invalid',
}
</script>

<template>
  <div class="settings-page">
    <div class="settings-card">
      <!-- 返回按钮 -->
      <button class="back-btn" @click="emit('go-back')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"/>
          <polyline points="12 19 5 12 12 5"/>
        </svg>
        返回首页
      </button>

      <h1 class="settings-title">Cookie 设置</h1>

      <!-- 当前状态 -->
      <div class="status-bar" :class="statusClass[cookieStatus]">
        当前状态：{{ statusLabel[cookieStatus] }}
      </div>

      <!-- 使用说明 -->
      <div class="guide-section">
        <h3 class="guide-title">如何获取小红书 Cookie</h3>
        <ol class="guide-steps">
          <li>打开 <strong>xiaohongshu.com</strong> 并登录</li>
          <li>按 <strong>F12</strong> 打开开发者工具</li>
          <li>切换到 <strong>Network</strong> 标签页，刷新页面</li>
          <li>找到任意请求，复制 Request Headers 中的 <strong>Cookie</strong> 完整内容</li>
          <li>粘贴到下方输入框中</li>
        </ol>
      </div>

      <!-- Cookie 输入 -->
      <div class="form-group">
        <label class="form-label">Cookie 内容</label>
        <textarea
          v-model="cookieText"
          class="form-textarea"
          rows="7"
          placeholder="请粘贴完整的小红书 Cookie 内容..."
        ></textarea>
      </div>

      <!-- 消息提示 -->
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <button
          class="btn btn-primary"
          :disabled="saving"
          @click="handleSave"
        >
          {{ saving ? '保存中...' : '保存 Cookie' }}
        </button>
        <button
          class="btn btn-secondary"
          :disabled="checking"
          @click="handleCheck"
        >
          {{ checking ? '检测中...' : '检测有效性' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  display: flex;
  justify-content: center;
  min-height: calc(100vh - 72px);
  padding: 40px 20px;
}

.settings-card {
  width: 100%;
  max-width: 600px;
  background: #FFFFFF;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 8px 24px rgba(0, 0, 0, 0.04);
}

.dark-mode .settings-card {
  background: #1C1B1B;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(0, 0, 0, 0.2);
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #F3F4F6;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #4A4A4A;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 20px;
}

.back-btn:hover {
  background: #E5E7EB;
  color: #121212;
}

.back-btn svg {
  width: 16px;
  height: 16px;
}

.dark-mode .back-btn {
  background: #2A2A2A;
  color: #9E9E9E;
}

.dark-mode .back-btn:hover {
  background: #3A3A3A;
  color: #E5E2E1;
}

.settings-title {
  font-size: 24px;
  font-weight: 700;
  color: #121212;
  margin: 0 0 20px;
}

.dark-mode .settings-title {
  color: #FFFFFF;
}

/* 状态条 */
.status-bar {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 24px;
}

.status-none {
  background: #F3F4F6;
  color: #6B7280;
}

.status-saved {
  background: #FEF3C7;
  color: #D97706;
}

.status-valid {
  background: #ECFDF5;
  color: #059669;
}

.status-invalid {
  background: #FEF2F2;
  color: #DC2626;
}

.dark-mode .status-none {
  background: #2A2A2A;
  color: #6B7280;
}

.dark-mode .status-saved {
  background: #422006;
  color: #FBBF24;
}

.dark-mode .status-valid {
  background: #064E3B;
  color: #6EE7B7;
}

.dark-mode .status-invalid {
  background: #7F1D1D;
  color: #FCA5A5;
}

/* 使用说明 */
.guide-section {
  background: #F9FAFB;
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.dark-mode .guide-section {
  background: #2A2A2A;
}

.guide-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 10px;
}

.dark-mode .guide-title {
  color: #D1D5DB;
}

.guide-steps {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #6B7280;
  line-height: 1.8;
}

.guide-steps strong {
  color: #374151;
}

.dark-mode .guide-steps {
  color: #9CA3AF;
}

.dark-mode .guide-steps strong {
  color: #D1D5DB;
}

/* 表单 */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.dark-mode .form-label {
  color: #D1D5DB;
}

.form-textarea {
  width: 100%;
  padding: 12px 14px;
  font-size: 13px;
  font-family: monospace;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  background: #F9FAFB;
  color: #111827;
  outline: none;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-textarea:focus {
  border-color: #E60023;
  box-shadow: 0 0 0 3px rgba(230, 0, 35, 0.08);
}

.dark-mode .form-textarea {
  background: #2A2A2A;
  border-color: #3A3A3A;
  color: #F3F4F6;
}

.dark-mode .form-textarea:focus {
  border-color: #FE2C55;
  box-shadow: 0 0 0 3px rgba(254, 44, 85, 0.15);
}

/* 消息 */
.message {
  padding: 10px 14px;
  font-size: 14px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.message.success {
  color: #059669;
  background: #ECFDF5;
}

.message.error {
  color: #DC2626;
  background: #FEF2F2;
}

.dark-mode .message.success {
  background: #064E3B;
  color: #6EE7B7;
}

.dark-mode .message.error {
  background: #7F1D1D;
  color: #FCA5A5;
}

/* 按钮 */
.actions {
  display: flex;
  gap: 12px;
}

.btn {
  flex: 1;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  color: #FFFFFF;
  background: #E60023;
}

.btn-primary:hover:not(:disabled) {
  background: #CC001F;
}

.btn-secondary {
  color: #E60023;
  background: #FFF1F2;
  border: 1px solid #FECDD3;
}

.btn-secondary:hover:not(:disabled) {
  background: #FFE4E6;
}

.dark-mode .btn-secondary {
  background: #3A1519;
  border-color: #5C2330;
  color: #FB7185;
}

.dark-mode .btn-secondary:hover:not(:disabled) {
  background: #4C1D25;
}
</style>
