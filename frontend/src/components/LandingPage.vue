<script setup lang="ts">
const emit = defineEmits<{
  (e: 'start-create'): void
}>()

const scrollToFeatures = () => {
  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
}

const scrollToBenefits = () => {
  document.getElementById('benefits')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-inner">
        <div class="hero-text">
          <h1 class="hero-title">
            红薯创作坊<br/>
            <span class="hero-highlight">让内容二创更简单、更专业</span>
          </h1>
          <p class="hero-desc">
            基于多模态 AI 技术，一键解析小红书链接，智能重塑文案与配图。
          </p>
          <div class="hero-actions">
            <button class="btn-primary" @click="emit('start-create')">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              免费开始
            </button>
            <button class="btn-secondary" @click="scrollToFeatures">
              了解更多
            </button>
          </div>
        </div>
        <div class="hero-visual">
          <div class="hero-preview-card">
            <div class="preview-header">
              <div class="preview-dots">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
              </div>
              <div class="preview-title">红薯创作坊</div>
            </div>
            <div class="preview-body">
              <div class="preview-input-row">
                <div class="preview-link-bar">
                  <svg class="preview-link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                  </svg>
                  <span class="preview-link-text">https://xiaohongshu.com/explore/...</span>
                </div>
                <div class="preview-btn">获取内容</div>
              </div>
              <div class="preview-cards-row">
                <div class="preview-card-item">
                  <div class="preview-card-label">原始笔记</div>
                  <div class="preview-card-thumb"></div>
                  <div class="preview-card-line"></div>
                  <div class="preview-card-line short"></div>
                </div>
                <div class="preview-arrow">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <polyline points="12 5 19 12 12 19"/>
                  </svg>
                </div>
                <div class="preview-card-item highlight">
                  <div class="preview-card-label">二创结果</div>
                  <div class="preview-card-thumb new"></div>
                  <div class="preview-card-line"></div>
                  <div class="preview-card-line short"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Benefits -->
    <section id="benefits" class="benefits-section">
      <div class="benefits-inner">
        <div class="benefit-card">
          <div class="benefit-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M3 3v18h18"/>
              <path d="M7 16l4-8 4 4 4-6"/>
            </svg>
          </div>
          <h3>智能解析</h3>
          <p>秒级提取原帖文案与视觉特征，深度挖掘爆款内容背后的核心逻辑。</p>
        </div>
        <div class="benefit-card" style="margin-top: 40px;">
          <div class="benefit-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </div>
          <h3>文案重塑</h3>
          <p>多种风格可选，保持品牌调性，通过 AI 算法实现文案的二次升华。</p>
        </div>
        <div class="benefit-card">
          <div class="benefit-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
          </div>
          <h3>多模态生图</h3>
          <p>识别原图特征，生成高匹配度新图，确保视觉风格的一致性与原创性。</p>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="features-section">
      <!-- Feature 1 -->
      <div class="feature-row">
        <div class="feature-visual">
          <div class="feature-demo analysis-demo">
            <div class="demo-header">AI 视觉分析</div>
            <div class="demo-content">
              <div class="demo-image-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>
              <div class="demo-analysis-tags">
                <span class="demo-tag">构图：三分法</span>
                <span class="demo-tag">色调：暖色系</span>
                <span class="demo-tag">风格：生活记录</span>
              </div>
            </div>
          </div>
        </div>
        <div class="feature-text">
          <span class="feature-label">核心技术</span>
          <h2>深度理解：AI 读懂原图构图与色调</h2>
          <p>
            不仅仅是简单的复制，我们的 AI 引擎能够解构图像的黄金分割比例、色彩平衡以及情绪表达，为您的二次创作提供精准的视觉基因。
          </p>
        </div>
      </div>

      <!-- Feature 2 -->
      <div class="feature-row reverse">
        <div class="feature-text">
          <span class="feature-label">效率工具</span>
          <h2>一键多方案：同时生成多个标题与文案</h2>
          <p>
            拒绝灵感枯竭。系统会根据您的需求，在几秒钟内提供从"深度共鸣"到"硬核干货"的不同侧重点文案方案，任您挑选。
          </p>
        </div>
        <div class="feature-visual">
          <div class="feature-demo titles-demo">
            <div class="demo-header">AI 文案生成</div>
            <div class="demo-content">
              <div class="demo-title-option selected">
                <span class="demo-badge">推荐</span>
                <span class="demo-title-text">深夜食堂 | 城市里最温暖的一碗面</span>
              </div>
              <div class="demo-title-option">
                <span class="demo-badge alt">情感</span>
                <span class="demo-title-text">一个人也要好好吃饭的 10 个理由</span>
              </div>
              <div class="demo-title-option">
                <span class="demo-badge alt">干货</span>
                <span class="demo-title-text">藏在巷子里的宝藏小店，本地人都知道</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Open Source -->
    <section class="oss-section">
      <div class="oss-inner">
        <h2>开源 & 免费</h2>
        <p class="oss-desc">
          红薯创作坊是完全开源的项目，你可以自由使用、修改和部署。无需注册，无需付费，本地运行即可。
        </p>
        <div class="oss-tech-stack">
          <span class="tech-tag">Vue 3</span>
          <span class="tech-tag">FastAPI</span>
          <span class="tech-tag">智谱 AI</span>
          <span class="tech-tag">多模态生图</span>
          <span class="tech-tag">WebSocket</span>
        </div>
        <div class="oss-actions">
          <a class="btn-primary" href="https://github.com/GGBOggbo/xhs-recreator" target="_blank" rel="noopener">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </a>
          <button class="btn-secondary" @click="emit('start-create')">
            开始使用
          </button>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="cta-inner">
        <h2>准备好开启内容创作的新纪元了吗？</h2>
        <p>粘贴小红书链接，30 秒完成一次完整的二创。</p>
        <button class="btn-primary btn-large" @click="emit('start-create')">
          立即开始
        </button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="landing-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="footer-logo">红薯创作坊</div>
          <p>助力每一位创作者，将创意无限放大。</p>
        </div>
        <div class="footer-links">
          <div>
            <h4>产品</h4>
            <ul>
              <li><a href="#features">功能介绍</a></li>
              <li><a href="https://github.com/GGBOggbo/xhs-recreator" target="_blank" rel="noopener">GitHub</a></li>
            </ul>
          </div>
          <div>
            <h4>技术</h4>
            <ul>
              <li><a href="#benefits">AI 解析</a></li>
              <li><a href="#features">多模态生图</a></li>
            </ul>
          </div>
          <div>
            <h4>关于</h4>
            <ul>
              <li><a href="https://github.com/GGBOggbo/xhs-recreator" target="_blank" rel="noopener">开源协议</a></li>
            </ul>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        &copy; 2026 红薯创作坊. 开源项目 · MIT License
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* ============ Hero ============ */
.hero-section {
  padding: 80px 24px 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.hero-inner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-title {
  font-size: 48px;
  font-weight: 800;
  line-height: 1.15;
  color: var(--text-primary);
  margin: 0 0 24px;
}

.hero-highlight {
  color: var(--primary-color);
  font-size: 42px;
}

.hero-desc {
  font-size: 18px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0 0 36px;
  max-width: 480px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: var(--primary-gradient);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  box-shadow: var(--shadow-btn);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(230, 0, 35, 0.35);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-primary.btn-large {
  padding: 18px 48px;
  font-size: 18px;
  border-radius: 16px;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--border-color);
}

/* Hero Visual - 纯 CSS 模拟的产品截图 */
.hero-visual {
  perspective: 800px;
}

.hero-preview-card {
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  transform: rotate(2deg);
  transition: transform 0.4s ease;
}

.hero-preview-card:hover {
  transform: rotate(0deg);
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.preview-dots {
  display: flex;
  gap: 6px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-red { background: #ff5f57; }
.dot-yellow { background: #ffbd2e; }
.dot-green { background: #28ca42; }

.preview-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.preview-body {
  padding: 24px;
}

.preview-input-row {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.preview-link-bar {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-muted);
}

.preview-link-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.preview-btn {
  padding: 10px 20px;
  background: var(--primary-gradient);
  color: white;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.preview-cards-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-card-item {
  flex: 1;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.preview-card-item.highlight {
  background: rgba(230, 0, 35, 0.06);
  border: 1px solid rgba(230, 0, 35, 0.15);
}

.preview-card-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.preview-card-thumb {
  height: 80px;
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  border-radius: 8px;
  margin-bottom: 8px;
}

.preview-card-thumb.new {
  background: linear-gradient(135deg, #fecdd3 0%, #fda4af 100%);
}

.preview-card-line {
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  margin-bottom: 6px;
}

.preview-card-line.short {
  width: 60%;
}

.preview-arrow {
  color: var(--primary-color);
  flex-shrink: 0;
}

.preview-arrow svg {
  width: 20px;
  height: 20px;
}

/* ============ Benefits ============ */
.benefits-section {
  padding: 80px 24px;
  background: var(--bg-secondary);
}

.benefits-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.benefit-card {
  padding: 40px 32px;
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.3s, transform 0.3s;
}

.benefit-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-4px);
}

.benefit-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: rgba(230, 0, 35, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  color: var(--primary-color);
  transition: transform 0.3s;
}

.benefit-card:hover .benefit-icon {
  transform: scale(1.1);
}

.benefit-icon svg {
  width: 28px;
  height: 28px;
}

.benefit-card h3 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px;
}

.benefit-card p {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}

/* ============ Features ============ */
.features-section {
  padding: 80px 24px;
}

.feature-row {
  max-width: 1200px;
  margin: 0 auto 80px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.feature-row:last-child {
  margin-bottom: 0;
}

.feature-label {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: var(--primary-color);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.feature-text h2 {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px;
  line-height: 1.3;
}

.feature-text p {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin: 0;
}

.feature-visual {
  display: flex;
  justify-content: center;
}

/* Feature Demo Cards */
.feature-demo {
  width: 100%;
  max-width: 420px;
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.demo-header {
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.demo-content {
  padding: 20px;
}

.demo-image-placeholder {
  height: 180px;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.demo-analysis-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.demo-tag {
  padding: 6px 12px;
  background: rgba(230, 0, 35, 0.06);
  color: var(--primary-color);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid rgba(230, 0, 35, 0.12);
}

/* Titles Demo */
.demo-title-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 8px;
  transition: background 0.2s;
}

.demo-title-option:hover {
  background: var(--bg-secondary);
}

.demo-title-option.selected {
  background: rgba(230, 0, 35, 0.06);
  border: 1px solid rgba(230, 0, 35, 0.15);
}

.demo-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background: var(--primary-color);
  color: white;
  white-space: nowrap;
}

.demo-badge.alt {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.demo-title-text {
  font-size: 14px;
  color: var(--text-primary);
}

/* ============ Open Source ============ */
.oss-section {
  padding: 80px 24px;
  background: var(--bg-secondary);
}

.oss-inner {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.oss-inner h2 {
  font-size: 32px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 16px;
}

.oss-desc {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin: 0 0 24px;
}

.oss-tech-stack {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 32px;
}

.tech-tag {
  padding: 6px 16px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid var(--border-color);
}

.oss-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* ============ CTA ============ */
.cta-section {
  padding: 80px 24px;
}

.cta-inner {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  padding: 60px 40px;
  background: var(--primary-gradient);
  border-radius: 20px;
  color: white;
  position: relative;
  overflow: hidden;
}

.cta-inner::before {
  content: '';
  position: absolute;
  top: -80px;
  right: -80px;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
}

.cta-inner::after {
  content: '';
  position: absolute;
  bottom: -80px;
  left: -80px;
  width: 300px;
  height: 300px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 50%;
}

.cta-inner h2 {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 12px;
  position: relative;
  z-index: 1;
}

.cta-inner p {
  font-size: 18px;
  opacity: 0.9;
  margin: 0 0 28px;
  position: relative;
  z-index: 1;
}

.cta-inner .btn-primary {
  background: white;
  color: var(--primary-color);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 1;
}

.cta-inner .btn-primary:hover {
  background: #f9f9f9;
  transform: translateY(-2px);
}

/* ============ Footer ============ */
.landing-footer {
  padding: 48px 24px 24px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
}

.footer-logo {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.footer-brand p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.footer-links h4 {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px;
}

.footer-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 8px;
}

.footer-links a {
  font-size: 14px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--text-primary);
}

.footer-bottom {
  max-width: 1200px;
  margin: 32px auto 0;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}

/* ============ Responsive ============ */
@media (max-width: 768px) {
  .hero-section {
    padding: 40px 16px 40px;
  }

  .hero-inner {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-highlight {
    font-size: 28px;
  }

  .hero-desc {
    font-size: 16px;
  }

  .hero-preview-card {
    transform: none;
  }

  .benefits-section {
    padding: 48px 16px;
  }

  .benefits-inner {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .benefit-card {
    margin-top: 0 !important;
    padding: 28px 20px;
  }

  .features-section {
    padding: 48px 16px;
  }

  .feature-row,
  .feature-row.reverse {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .feature-text h2 {
    font-size: 24px;
  }

  .oss-section {
    padding: 48px 16px;
  }

  .oss-inner h2 {
    font-size: 24px;
  }

  .cta-section {
    padding: 48px 16px;
  }

  .cta-inner {
    padding: 40px 24px;
  }

  .cta-inner h2 {
    font-size: 24px;
  }

  .footer-inner {
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
}

/* ============ Dark mode ============ */
.dark-mode .benefit-card {
  background: var(--bg-primary);
  box-shadow: var(--shadow-lg);
}

.dark-mode .benefit-card:hover {
  box-shadow: 0 0 20px rgba(255, 81, 104, 0.15);
}

.dark-mode .feature-demo {
  background: var(--bg-primary);
}

.dark-mode .demo-image-placeholder {
  background: linear-gradient(135deg, #2A2A2A 0%, #353534 100%);
}

.dark-mode .demo-tag {
  background: rgba(255, 81, 104, 0.12);
  border-color: rgba(255, 81, 104, 0.25);
  color: var(--primary-color);
}

.dark-mode .demo-title-option.selected {
  background: rgba(255, 81, 104, 0.1);
  border-color: rgba(255, 81, 104, 0.2);
}

.dark-mode .demo-badge.alt {
  background: var(--bg-tertiary);
}

.dark-mode .tech-tag {
  background: var(--bg-primary);
  border-color: var(--border-color);
}

.dark-mode .landing-footer {
  background: #0D0D0D;
}

.dark-mode .oss-section {
  background: #0D0D0D;
}
</style>
