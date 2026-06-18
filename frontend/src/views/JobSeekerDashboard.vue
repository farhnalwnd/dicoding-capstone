<template>
  <div class="js-dashboard">

    <!-- Hero Welcome Banner -->
    <div class="welcome-banner glass-panel">
      <div class="banner-left">
        <div class="user-avatar-lg">{{ userInitial }}</div>
        <div class="banner-info">
          <div class="role-pill">
            <span class="pill-dot"></span>
            Job Seeker
          </div>
          <h1 class="welcome-title">Welcome back, <span class="name-highlight">{{ userName }}</span>!</h1>
          <p class="welcome-sub">Your AI-powered career toolkit is ready. What would you like to do today?</p>
        </div>
      </div>
      <div class="banner-deco" aria-hidden="true">
        <span class="deco-circle c1"></span>
        <span class="deco-circle c2"></span>
      </div>
    </div>

    <!-- Feature Cards — horizontal row -->
    <section class="features-section">
      <h2 class="features-heading">Quick Actions</h2>

      <div class="features-row">
        <!-- Check Resume -->
        <router-link to="/jobseeker/analyze" class="feature-card glass-panel check-resume-card">
          <div class="fc-icon-wrap fc-teal">
            <span class="fc-icon">📄</span>
          </div>
          <div class="fc-body">
            <h3 class="fc-title">Check Resume</h3>
            <p class="fc-desc">Analyze how your CV matches a job description using AI semantic scoring.</p>
            <span class="fc-cta">Analyze Now <span class="cta-arrow">→</span></span>
          </div>
        </router-link>

        <!-- Job Scraper -->
        <router-link to="/jobseeker/scrape" class="feature-card glass-panel job-scraper-card">
          <div class="fc-icon-wrap fc-indigo">
            <span class="fc-icon">🔍</span>
          </div>
          <div class="fc-body">
            <h3 class="fc-title">Job Scraper</h3>
            <p class="fc-desc">Discover real job opportunities from LinkedIn by keywords &amp; location.</p>
            <span class="fc-cta">Find Jobs <span class="cta-arrow">→</span></span>
          </div>
        </router-link>

        <!-- AI Resume Advisor -->
        <router-link to="/resume-advisor" class="feature-card glass-panel advisor-card">
          <div class="fc-icon-wrap fc-purple">
            <span class="fc-icon">🤖</span>
          </div>
          <div class="fc-body">
            <h3 class="fc-title">AI Resume Advisor</h3>
            <p class="fc-desc">Get a personalized career roadmap &amp; resume tips powered by Gemini AI.</p>
            <span class="fc-cta fc-cta-purple">Open Advisor <span class="cta-arrow">→</span></span>
          </div>
        </router-link>
      </div>
    </section>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { authState } from '../stores/auth'

const user = computed(() => authState.user || {})
const userName = computed(() => user.value.name || 'User')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())
</script>

<style scoped>
/* ===== Layout ===== */
.js-dashboard {
  max-width: 1160px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* ===== Welcome Banner ===== */
.welcome-banner {
  padding: 2.4rem 2.8rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  overflow: hidden;
  position: relative;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 1.6rem;
  flex: 1;
}

.user-avatar-lg {
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent) 0%, var(--indigo) 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 800;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(14, 165, 164, 0.3);
}

.banner-info {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.role-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(14, 165, 164, 0.1);
  border: 1px solid rgba(14, 165, 164, 0.25);
  border-radius: 999px;
  padding: 0.25rem 0.65rem;
  width: fit-content;
}

.pill-dot {
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 50%;
  background: #22C55E;
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.18);
}

.welcome-title {
  font-size: clamp(1.2rem, 2.5vw, 1.5rem);
  font-weight: 800;
  color: var(--text);
  margin: 0;
  line-height: 1.25;
}

.name-highlight {
  color: var(--accent);
}

.welcome-sub {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.5;
}

/* Decorative circles */
.banner-deco {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.06;
}
.c1 {
  width: 180px; height: 180px;
  background: var(--accent);
  right: -40px; top: -60px;
}
.c2 {
  width: 120px; height: 120px;
  background: var(--indigo);
  right: 80px; bottom: -50px;
}

/* ===== Features Section ===== */
.features-heading {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 1.2rem;
}

.features-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

/* ===== Feature Card ===== */
.feature-card {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  padding: 1.8rem 1.6rem;
  text-decoration: none;
  color: inherit;
  border-radius: var(--radius-lg);
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

/* Card accent borders */
.check-resume-card:hover { border-color: var(--accent); }
.job-scraper-card:hover  { border-color: var(--indigo); }
.advisor-card            { border-color: rgba(124, 58, 237, 0.18); }
.advisor-card:hover      { border-color: var(--purple); }

/* Icon wrap */
.fc-icon-wrap {
  width: 3.2rem;
  height: 3.2rem;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}
.fc-teal   { background: rgba(14, 165, 164, 0.1);  border: 1px solid rgba(14, 165, 164, 0.2);  }
.fc-indigo { background: rgba(79, 70, 229, 0.1);   border: 1px solid rgba(79, 70, 229, 0.2);   }
.fc-purple { background: rgba(124, 58, 237, 0.1);  border: 1px solid rgba(124, 58, 237, 0.2);  }

.fc-body {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  flex: 1;
}

.fc-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text);
  margin: 0;
}

.fc-desc {
  font-size: 0.86rem;
  line-height: 1.55;
  color: var(--text-muted);
  margin: 0;
  flex: 1;
}

.fc-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.84rem;
  font-weight: 700;
  color: var(--accent);
  margin-top: 0.5rem;
  transition: gap 0.2s ease;
}
.fc-cta-purple { color: var(--purple); }
.feature-card:hover .fc-cta { gap: 0.5rem; }

.cta-arrow {
  transition: transform 0.2s ease;
}
.feature-card:hover .cta-arrow { transform: translateX(3px); }

/* ===== Responsive ===== */
@media (max-width: 900px) {
  .features-row {
    grid-template-columns: 1fr;
  }
  .welcome-banner {
    padding: 1.8rem 1.6rem;
  }
  .user-avatar-lg {
    width: 3.5rem;
    height: 3.5rem;
    font-size: 1.5rem;
  }
}

@media (max-width: 580px) {
  .banner-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  .welcome-title {
    font-size: 1.1rem;
  }
  .welcome-banner {
    padding: 1.4rem 1.2rem;
  }
  .feature-card {
    padding: 1.4rem 1.2rem;
  }
}
</style>
