<script setup lang="ts">
import { ref, computed } from 'vue'
import { authApi, login as authLogin } from '../utils/auth'

const emit = defineEmits<{
  (e: 'login-success', data: { has_cookie: boolean }): void
  (e: 'close'): void
}>()

const mode = ref<'login' | 'register'>('login')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const successMsg = ref('')

const canSubmit = computed(() => {
  if (!username.value || username.value.length < 3) return false
  if (!password.value || password.value.length < 6) return false
  if (mode.value === 'register' && password.value !== confirmPassword.value) return false
  return true
})

const switchMode = () => {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  error.value = ''
  successMsg.value = ''
}

const handleSubmit = async () => {
  if (!canSubmit.value || loading.value) return

  loading.value = true
  error.value = ''
  successMsg.value = ''

  try {
    if (mode.value === 'register') {
      await authApi.register({ username: username.value, password: password.value })
      successMsg.value = '注册成功，请登录'
      mode.value = 'login'
      password.value = ''
      confirmPassword.value = ''
    } else {
      const res = await authApi.login({ username: username.value, password: password.value })
      const { token, user } = res.data.data
      authLogin(token, user)
      emit('login-success', { has_cookie: user.has_cookie })
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <!-- 关闭按钮 -->
      <button class="login-close-btn" @click="emit('close')" title="关闭">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
      <!-- 品牌标识 -->
      <div class="login-brand">
        <h1 class="login-title">红薯创作坊</h1>
        <p class="login-subtitle">AI 驱动的小红书内容二创平台</p>
      </div>

      <!-- Tab 切换 -->
      <div class="login-tabs">
        <button
          class="tab-btn"
          :class="{ active: mode === 'login' }"
          @click="mode = 'login'; error = ''; successMsg = ''"
        >
          登录
        </button>
        <button
          class="tab-btn"
          :class="{ active: mode === 'register' }"
          @click="mode = 'register'; error = ''; successMsg = ''"
        >
          注册
        </button>
      </div>

      <!-- 表单 -->
      <form class="login-form" @submit.prevent="handleSubmit">
        <!-- 成功提示 -->
        <div v-if="successMsg" class="success-msg">{{ successMsg }}</div>

        <!-- 错误提示 -->
        <div v-if="error" class="error-msg">{{ error }}</div>

        <div class="form-group">
          <label class="form-label">用户名</label>
          <input
            v-model="username"
            type="text"
            class="form-input"
            placeholder="3-20 个字符"
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="password"
            type="password"
            class="form-input"
            placeholder="至少 6 位"
            autocomplete="current-password"
          />
        </div>

        <div v-if="mode === 'register'" class="form-group">
          <label class="form-label">确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="form-input"
            placeholder="再次输入密码"
            autocomplete="new-password"
          />
          <p v-if="confirmPassword && password !== confirmPassword" class="field-error">
            两次密码不一致
          </p>
        </div>

        <button
          type="submit"
          class="submit-btn"
          :disabled="!canSubmit || loading"
        >
          {{ loading ? '处理中...' : (mode === 'login' ? '登 录' : '注 册') }}
        </button>
      </form>

      <!-- 底部切换链接 -->
      <p class="switch-hint">
        {{ mode === 'login' ? '还没有账号？' : '已有账号？' }}
        <a href="#" @click.prevent="switchMode">
          {{ mode === 'login' ? '立即注册' : '去登录' }}
        </a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 72px);
  padding: 20px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 200;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: #FFFFFF;
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 8px 24px rgba(0, 0, 0, 0.04);
  position: relative;
}

.login-close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: #9CA3AF;
  border-radius: 8px;
  transition: all 0.2s;
}

.login-close-btn:hover {
  background: #F3F4F6;
  color: #374151;
}

.login-close-btn svg {
  width: 18px;
  height: 18px;
}

.dark-mode .login-close-btn:hover {
  background: #2A2A2A;
  color: #E5E2E1;
}

.dark-mode .login-card {
  background: #1C1B1B;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(0, 0, 0, 0.2);
}

.login-brand {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #E60023;
  margin: 0 0 8px;
}

.dark-mode .login-title {
  color: #FE2C55;
}

.login-subtitle {
  font-size: 14px;
  color: #6B7280;
  margin: 0;
}

.dark-mode .login-subtitle {
  color: #9CA3AF;
}

.login-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  border-bottom: 2px solid #F3F4F6;
}

.dark-mode .login-tabs {
  border-bottom-color: #2A2A2A;
}

.tab-btn {
  flex: 1;
  padding: 10px 0;
  font-size: 15px;
  font-weight: 500;
  color: #9CA3AF;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  color: #E60023;
  border-bottom-color: #E60023;
}

.dark-mode .tab-btn.active {
  color: #FE2C55;
  border-bottom-color: #FE2C55;
}

.tab-btn:hover:not(.active) {
  color: #6B7280;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.dark-mode .form-label {
  color: #D1D5DB;
}

.form-input {
  height: 44px;
  padding: 0 14px;
  font-size: 15px;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  background: #F9FAFB;
  color: #111827;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  border-color: #E60023;
  box-shadow: 0 0 0 3px rgba(230, 0, 35, 0.08);
}

.dark-mode .form-input {
  background: #2A2A2A;
  border-color: #3A3A3A;
  color: #F3F4F6;
}

.dark-mode .form-input:focus {
  border-color: #FE2C55;
  box-shadow: 0 0 0 3px rgba(254, 44, 85, 0.15);
}

.field-error {
  font-size: 12px;
  color: #EF4444;
  margin: 0;
}

.success-msg {
  padding: 10px 14px;
  font-size: 14px;
  color: #059669;
  background: #ECFDF5;
  border-radius: 8px;
}

.dark-mode .success-msg {
  background: #064E3B;
  color: #6EE7B7;
}

.error-msg {
  padding: 10px 14px;
  font-size: 14px;
  color: #DC2626;
  background: #FEF2F2;
  border-radius: 8px;
}

.dark-mode .error-msg {
  background: #7F1D1D;
  color: #FCA5A5;
}

.submit-btn {
  height: 44px;
  margin-top: 4px;
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
  background: #E60023;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #CC001F;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.switch-hint {
  text-align: center;
  font-size: 14px;
  color: #9CA3AF;
  margin: 20px 0 0;
}

.switch-hint a {
  color: #E60023;
  text-decoration: none;
  font-weight: 500;
}

.dark-mode .switch-hint a {
  color: #FE2C55;
}

.switch-hint a:hover {
  text-decoration: underline;
}
</style>
