<template>
  <div class="landing-page">
    <section class="hero">
      <div class="container hero-content">
        <div class="hero-text">
          <h1 class="hero-title animate-fadeIn">
            <span class="gradient-text">PromptUI</span>
          </h1>
          <p class="hero-subtitle animate-fadeIn" style="animation-delay: 0.1s">
            专业的前端 UI 提示词素材库
          </p>
          <p class="hero-description animate-fadeIn" style="animation-delay: 0.2s">
            覆盖布局、卡片、组件、动效、配色五大类别，
            帮你快速生成可落地的前端界面。
          </p>
          <div class="hero-actions animate-fadeIn" style="animation-delay: 0.3s">
            <router-link to="/layouts" class="btn btn-primary btn-large">
              探索素材库
            </router-link>
            <router-link to="/cards" class="btn btn-secondary btn-large">
              查看卡片示例
            </router-link>
          </div>
        </div>

        <div class="hero-visual animate-slideUp">
          <div class="preview-card">
            <div class="preview-header">
              <div class="preview-dots">
                <span></span><span></span><span></span>
              </div>
              <div class="preview-title">Prompt Snippet</div>
            </div>
            <div class="preview-content">
              <div class="code-line"><span class="code-keyword">const</span> <span class="code-var">layout</span> = <span class="code-string">"运营中台侧栏"</span></div>
              <div class="code-line"><span class="code-keyword">const</span> <span class="code-var">card</span> = <span class="code-string">"门店补货商品卡"</span></div>
              <div class="code-line"><span class="code-keyword">const</span> <span class="code-var">motion</span> = <span class="code-string">"卡片悬浮抬升"</span></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="container">
        <h2 class="section-title">为什么选择 PromptUI</h2>
        <div class="features-grid">
          <div class="feature-card">
            <h3>分类清晰</h3>
            <p>布局、卡片、组件、动效、配色按场景拆分，检索效率高。</p>
          </div>
          <div class="feature-card">
            <h3>复制即用</h3>
            <p>每条提示词可一键复制，直接用于你的 AI 编程工作流。</p>
          </div>
          <div class="feature-card">
            <h3>可视化预览</h3>
            <p>每个条目带预览组件，阅读提示词前先看效果。</p>
          </div>
        </div>
      </div>
    </section>

    <section class="stats">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">100+</div>
            <div class="stat-label">提示词条目</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">5</div>
            <div class="stat-label">核心分类</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">1 Click</div>
            <div class="stat-label">复制使用</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  min-height: calc(100vh - var(--navbar-height));
  display: flex;
  align-items: center;
  padding: var(--spacing-3xl) 0;
  background:
    radial-gradient(900px 380px at 8% -10%, color-mix(in srgb, var(--color-primary) 8%, transparent), transparent 62%),
    radial-gradient(760px 320px at 100% 110%, color-mix(in srgb, var(--color-primary) 10%, transparent), transparent 65%),
    linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-3xl);
  align-items: center;
}

.hero-text { max-width: 600px; }

.hero-title {
  font-size: var(--font-size-5xl);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: var(--spacing-lg);
  letter-spacing: -0.02em;
}

.gradient-text {
  background: linear-gradient(135deg, #000000 0%, #404040 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: var(--font-size-2xl);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
  font-weight: 600;
}

.hero-description {
  font-size: var(--font-size-lg);
  color: var(--text-tertiary);
  line-height: 1.7;
  margin-bottom: var(--spacing-2xl);
}

.hero-actions { display: flex; gap: var(--spacing-md); flex-wrap: wrap; }
.btn-large { padding: 1rem 2rem; font-size: var(--font-size-base); }

.btn-secondary {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.hero-visual { display: flex; justify-content: center; align-items: center; }

.preview-card {
  width: 100%;
  max-width: 500px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.preview-dots { display: flex; gap: 6px; }
.preview-dots span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--border-color-strong);
}

.preview-title { font-size: var(--font-size-sm); font-weight: 600; color: var(--text-secondary); }

.preview-content {
  padding: var(--spacing-xl);
  font-family: 'Menlo', 'Consolas', monospace;
  font-size: var(--font-size-sm);
  line-height: 2;
}

.code-line { margin-bottom: var(--spacing-sm); }
.code-keyword { color: var(--text-primary); font-weight: 700; }
.code-var { color: var(--text-secondary); }
.code-string { color: var(--text-tertiary); }

.features { padding: var(--spacing-3xl) 0; background: var(--bg-primary); }
.section-title { font-size: var(--font-size-3xl); font-weight: 700; text-align: center; margin-bottom: var(--spacing-2xl); }
.features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--spacing-xl); }

.feature-card {
  padding: var(--spacing-xl);
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}

.feature-card h3 { font-size: var(--font-size-xl); margin-bottom: var(--spacing-sm); }
.feature-card p { color: var(--text-secondary); line-height: 1.6; }

.stats { padding: var(--spacing-3xl) 0; background: var(--bg-tertiary); }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-xl); }
.stat-item { text-align: center; }
.stat-number { font-size: var(--font-size-4xl); font-weight: 800; color: var(--color-primary); }
.stat-label { color: var(--text-secondary); margin-top: var(--spacing-sm); }

[data-theme='dark'] .hero {
  background:
    radial-gradient(900px 380px at 8% -10%, rgba(255, 255, 255, 0.06), transparent 62%),
    radial-gradient(760px 320px at 100% 110%, rgba(255, 255, 255, 0.04), transparent 65%),
    linear-gradient(135deg, #090909 0%, #121212 100%);
}

[data-theme='dark'] .gradient-text {
  background: linear-gradient(135deg, #ffffff 0%, #bfbfbf 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

[data-theme='dark'] .btn-secondary {
  background: #121212;
  border-color: var(--border-color-strong);
}

@media (max-width: 968px) {
  .hero-content { grid-template-columns: 1fr; gap: var(--spacing-2xl); }
  .hero-visual { order: -1; }
  .hero-title { font-size: var(--font-size-4xl); }
}

@media (max-width: 640px) {
  .hero-actions { flex-direction: column; }
  .hero-actions .btn { width: 100%; }
}
</style>
