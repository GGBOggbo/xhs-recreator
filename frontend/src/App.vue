<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import LinkInput from './components/LinkInput.vue'
import LandingPage from './components/LandingPage.vue'
import LoginPage from './components/LoginPage.vue'
import SettingsPage from './components/SettingsPage.vue'
import PreviewConfig from './components/PreviewConfig.vue'
import ProgressPanel from './components/ProgressPanel.vue'
import ResultDisplay from './components/ResultDisplay.vue'
import HistoryList from './components/HistoryList.vue'
import { isAuthenticated, getCurrentUser, logout } from './utils/auth'

// 状态
const currentTaskId = ref<string>('')
const currentStep = ref<'login' | 'landing' | 'input' | 'preview' | 'processing' | 'result' | 'history' | 'settings'>('landing')
const originalContent = ref<any>(null)
const generatedResult = ref<any>(null)

// 夜间模式
const isDarkMode = ref(false)

// 当前用户名
const currentUser = computed(() => getCurrentUser())
const displayUsername = computed(() => {
  const name = currentUser.value?.username as string
  if (!name) return ''
  return name.length > 6 ? name.slice(0, 6) + '...' : name
})

// 初始化 - 恢复页面状态
onMounted(() => {
  // 恢复夜间模式
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDarkMode.value = true
    document.documentElement.classList.add('dark')
  }

  // 始终从 landing 开始，除非已登录且上次在创作流程中
  if (isAuthenticated()) {
    const savedStep = sessionStorage.getItem('xhs_step')
    if (savedStep && ['input', 'preview', 'processing', 'result', 'settings'].includes(savedStep)) {
      currentStep.value = savedStep as any
    } else {
      currentStep.value = 'landing'
    }
  } else {
    currentStep.value = 'landing'
  }

  // 恢复页面状态
  const savedTaskId = sessionStorage.getItem('xhs_task_id')
  const savedContent = sessionStorage.getItem('xhs_content')
  const savedResult = sessionStorage.getItem('xhs_result')

  if (savedTaskId) {
    currentTaskId.value = savedTaskId
  }
  if (savedContent) {
    try {
      originalContent.value = JSON.parse(savedContent)
    } catch (e) {}
  }
  if (savedResult) {
    try {
      generatedResult.value = JSON.parse(savedResult)
    } catch (e) {}
  }
})

// 持久化状态到 sessionStorage
watch(currentStep, (val) => {
  sessionStorage.setItem('xhs_step', val)
})

watch(currentTaskId, (val) => {
  if (val) {
    sessionStorage.setItem('xhs_task_id', val)
  } else {
    sessionStorage.removeItem('xhs_task_id')
  }
})

watch(originalContent, (val) => {
  if (val) {
    sessionStorage.setItem('xhs_content', JSON.stringify(val))
  } else {
    sessionStorage.removeItem('xhs_content')
  }
}, { deep: true })

watch(generatedResult, (val) => {
  if (val) {
    sessionStorage.setItem('xhs_result', JSON.stringify(val))
  } else {
    sessionStorage.removeItem('xhs_result')
  }
}, { deep: true })

// 切换夜间模式
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// 处理爬取完成 - 进入预览阶段
const handleFetched = (content: any) => {
  originalContent.value = content
  currentStep.value = 'preview'
}

// 处理开始二创 - 进入处理阶段
const handleStartRecreate = (taskId: string) => {
  currentTaskId.value = taskId
  currentStep.value = 'processing'
}

// 处理任务完成
const handleTaskComplete = (result: any) => {
  generatedResult.value = result
  currentStep.value = 'result'
}

// 返回输入阶段
const handleBackToInput = () => {
  currentStep.value = 'input'
  originalContent.value = null
}

// 从落地页进入创作 - 需要检查登录态
const showLoginPage = ref(false)
const handleStartCreate = () => {
  if (isAuthenticated()) {
    currentStep.value = 'input'
  } else {
    showLoginPage.value = true
  }
}

const closeLoginPage = () => {
  showLoginPage.value = false
}

// 品牌点击 - 回到落地页
const handleBrandClick = () => {
  if (currentStep.value !== 'landing') {
    handleReset()
    currentStep.value = 'landing'
  }
}

// 重新开始
const handleReset = () => {
  currentTaskId.value = ''
  currentStep.value = 'input'
  originalContent.value = null
  generatedResult.value = null
  // 清除 sessionStorage
  sessionStorage.removeItem('xhs_step')
  sessionStorage.removeItem('xhs_task_id')
  sessionStorage.removeItem('xhs_content')
  sessionStorage.removeItem('xhs_result')
}

// 导航到历史记录
const goToHistory = () => {
  currentStep.value = 'history'
}

// 从历史记录返回
const backFromHistory = () => {
  currentStep.value = 'landing'
}

// 登录成功处理
const handleLoginSuccess = (data: { has_cookie: boolean }) => {
  showLoginPage.value = false
  currentStep.value = 'input'
}
</script>

<template>
  <div class="app" :class="{ 'dark-mode': isDarkMode }">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-inner">
        <!-- 左侧品牌 -->
        <div class="brand" @click="handleBrandClick">红薯创作坊</div>

        <!-- 中间导航 -->
        <nav class="nav-menu">
          <button
            class="nav-item"
            :class="{ active: currentStep === 'landing' }"
            @click="handleBrandClick"
          >
            首页
          </button>
          <button
            class="nav-item"
            :class="{ active: currentStep !== 'landing' && currentStep !== 'history' }"
            @click="handleReset"
          >
            开始创作
          </button>
          <button
            class="nav-item"
            :class="{ active: currentStep === 'history' }"
            @click="goToHistory"
          >
            历史记录
          </button>
          <button class="nav-item" disabled>
            创作灵感
          </button>
        </nav>

        <!-- 右侧操作区 -->
        <div class="header-actions">
          <!-- 夜间模式切换 -->
          <button class="header-icon-btn theme-toggle" :title="isDarkMode ? '切换日间模式' : '切换夜间模式'" @click="toggleDarkMode">
            <svg v-if="!isDarkMode" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="5"/>
              <line x1="12" y1="1" x2="12" y2="3"/>
              <line x1="12" y1="21" x2="12" y2="23"/>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
              <line x1="1" y1="12" x2="3" y2="12"/>
              <line x1="21" y1="12" x2="23" y2="12"/>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>
          <!-- 未登录：显示登录按钮 -->
          <button v-if="!isAuthenticated()" class="login-header-btn" @click="showLoginPage = true">
            登录
          </button>
          <!-- 已登录：用户名 + 设置 + 注销 -->
          <template v-else>
            <span class="username">{{ displayUsername }}</span>
            <button class="header-icon-btn" title="Cookie 设置" @click="currentStep = 'settings'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
            </button>
            <button class="header-icon-btn logout-btn" title="退出登录" @click="logout()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
            </button>
          </template>
        </div>
      </div>
    </header>

    <main class="main-content">
      <!-- 落地页（始终显示） -->
      <LandingPage
        v-if="currentStep === 'landing'"
        @start-create="handleStartCreate"
      />

      <!-- 设置页 -->
      <SettingsPage
        v-else-if="currentStep === 'settings'"
        @go-back="currentStep = 'landing'"
      />

      <!-- 历史记录页面 -->
      <template v-else-if="currentStep === 'history'">
        <div class="history-page">
          <div class="history-page-header">
            <button class="back-btn" @click="backFromHistory">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="19" y1="12" x2="5" y2="12"/>
                <polyline points="12 19 5 12 12 5"/>
              </svg>
              返回
            </button>
            <h1 class="page-title">历史记录</h1>
          </div>
          <HistoryList />
        </div>
      </template>

      <!-- 主流程页面 -->
      <template v-else-if="currentStep === 'input' || currentStep === 'preview' || currentStep === 'processing' || currentStep === 'result'">
        <!-- Step 1: 输入链接 -->
        <LinkInput
          v-if="currentStep === 'input'"
          @fetched="handleFetched"
        />

        <!-- Step 2: 预览原始内容 + 配置参数 -->
        <PreviewConfig
          v-else-if="currentStep === 'preview'"
          :content="originalContent"
          @start-recreate="handleStartRecreate"
          @back="handleBackToInput"
        />

        <!-- Step 3: 处理中 -->
        <template v-else-if="currentStep === 'processing'">
          <ProgressPanel
            :task-id="currentTaskId"
            @complete="handleTaskComplete"
            @reset="handleReset"
          />
        </template>

        <!-- Step 4: 结果展示 -->
        <ResultDisplay
          v-else-if="currentStep === 'result'"
          :original="originalContent"
          :result="generatedResult"
          @reset="handleReset"
        />
      </template>

      <!-- 登录弹窗 -->
      <LoginPage
        v-if="showLoginPage"
        @login-success="handleLoginSuccess"
        @close="closeLoginPage"
      />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: #F8FAFC;
  position: relative;
  overflow-x: hidden;
  transition: background 0.3s ease;
}

/* 夜间模式 - 参考专业设计 */
.app.dark-mode {
  background: #131313;
}

.dark-mode .header {
  background: #131313;
  border-bottom-color: transparent;
}

.dark-mode .brand {
  color: #FE2C55;
}

.dark-mode .nav-item {
  color: #E5E2E1;
  opacity: 0.7;
}

.dark-mode .nav-item:hover:not(:disabled) {
  color: #FE2C55;
  opacity: 1;
}

.dark-mode .nav-item.active {
  color: #FE2C55;
  opacity: 1;
  font-weight: 700;
}

.dark-mode .header-icon-btn {
  color: #E5E2E1;
  opacity: 0.7;
}

.dark-mode .header-icon-btn:hover {
  background: #1C1B1B;
  color: #E5E2E1;
  opacity: 1;
}

.dark-mode::before {
  background: radial-gradient(circle, rgba(255, 81, 104, 0.05) 0%, transparent 50%);
}

.dark-mode::after {
  background: radial-gradient(circle, rgba(255, 81, 104, 0.05) 0%, transparent 50%);
}

/* 背景渐变 */
.app::before {
  content: '';
  position: fixed;
  top: -200px;
  right: -200px;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(244, 114, 182, 0.08) 0%, transparent 70%);
  pointer-events: none;
  transition: background 0.3s ease;
}

.app::after {
  content: '';
  position: fixed;
  bottom: -200px;
  left: -200px;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(52, 211, 153, 0.06) 0%, transparent 70%);
  pointer-events: none;
  transition: background 0.3s ease;
}

/* 顶部导航栏 */
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #FFFFFF;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background 0.3s ease, border-color 0.3s ease;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  height: 72px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  font-size: 20px;
  font-weight: 700;
  color: #E60023;
  letter-spacing: -0.5px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.brand:hover {
  opacity: 0.8;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-item {
  font-size: 16px;
  font-weight: 400;
  color: #4A4A4A;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px 0;
  position: relative;
  transition: color 0.2s;
}

.nav-item:hover:not(:disabled) {
  color: #121212;
}

.nav-item.active {
  font-weight: 600;
  color: #E60023;
}

.nav-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: #6B7280;
  border-radius: 8px;
  transition: all 0.2s;
}

.header-icon-btn:hover {
  background: #F3F4F6;
  color: #121212;
}

.header-icon-btn svg {
  width: 20px;
  height: 20px;
}

.theme-toggle {
  background: #FEF3C7;
  color: #D97706;
}

.theme-toggle:hover {
  background: #FDE68A;
  color: #B45309;
}

.dark-mode .theme-toggle {
  background: #1C1B1B;
  color: #9E9E9E;
}

.dark-mode .theme-toggle:hover {
  background: #2A2A2A;
  color: #E5E2E1;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dark-mode .username {
  color: #D1D5DB;
}

.login-header-btn {
  padding: 6px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #FFFFFF;
  background: #E60023;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.login-header-btn:hover {
  background: #CC001F;
}

.dark-mode .login-header-btn {
  background: #FE2C55;
}

.dark-mode .login-header-btn:hover {
  background: #EF1139;
}

.logout-btn {
  color: #9CA3AF;
}

.logout-btn:hover {
  color: #EF4444;
  background: #FEF2F2;
}

.dark-mode .logout-btn {
  color: #6B7280;
}

.dark-mode .logout-btn:hover {
  color: #F87171;
  background: #7F1D1D;
}

.main-content {
  position: relative;
  z-index: 1;
  padding-bottom: 60px;
}

/* 历史记录页面 */
.history-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.history-page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  display: flex;
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
}

.back-btn:hover {
  background: #E5E7EB;
  color: #121212;
}

.back-btn svg {
  width: 16px;
  height: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #121212;
  margin: 0;
}

.dark-mode .back-btn {
  background: #1C1B1B;
  color: #9E9E9E;
}

.dark-mode .back-btn:hover {
  background: #2A2A2A;
  color: #E5E2E1;
}

.dark-mode .page-title {
  color: #FFFFFF;
}

/* 响应式 */
@media (max-width: 768px) {
  .header-inner {
    padding: 0 16px;
    height: 64px;
  }

  .brand {
    font-size: 18px;
  }

  .nav-menu {
    gap: 16px;
  }

  .nav-item {
    font-size: 14px;
  }

  .header-actions {
    gap: 8px;
  }

  /* 移动端隐藏部分导航 */
  .nav-item:nth-child(3) {
    display: none;
  }

  .username {
    display: none;
  }

  .history-page {
    padding: 24px 16px;
  }

  .page-title {
    font-size: 24px;
  }
}
</style>
