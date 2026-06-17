<template>
  <div class="home-container">
    <section class="hero-section glass-panel">
      <div class="hero-copy">
        <span class="hero-badge">
          <span class="badge-dot"></span>
          AI Recruitment Assistant
        </span>

        <h1>Welcome to HIREZY</h1>
        <p>
          Match CVs with job descriptions, rank candidates, and discover relevant skills through a simple AI-powered recruitment workflow.
        </p>

        <div class="hero-actions">
          <router-link to="/jobseeker/analyze" class="hero-btn primary">
            Analyze CV
            <span>→</span>
          </router-link>
          <router-link to="/hr/rank" class="hero-btn secondary">
            HR Ranking
          </router-link>
        </div>
      </div>

      <div class="workflow-preview" aria-label="HIREZY workflow preview">
        <div class="preview-glow"></div>

        <div class="preview-header">
          <div>
            <span class="preview-kicker">Workflow Preview</span>
            <h2>Smart CV Screening</h2>
          </div>
          <div class="status-pill">Ready</div>
        </div>

        <div class="workflow-steps">
          <div class="workflow-card cv-card">
            <span class="step-number">01</span>
            <div class="step-icon">📄</div>
            <div>
              <h3>Upload CV</h3>
              <p>PDF/DOCX candidate profile</p>
            </div>
          </div>

          <div class="connector-line"></div>

          <div class="workflow-card analysis-card">
            <span class="step-number">02</span>
            <div class="step-icon">🧠</div>
            <div>
              <h3>AI Matching</h3>
              <p>Semantic score and domain skills</p>
            </div>
          </div>

          <div class="connector-line"></div>

          <div class="workflow-card rank-card">
            <span class="step-number">03</span>
            <div class="step-icon">🏆</div>
            <div>
              <h3>Rank Candidates</h3>
              <p>Sorted results for HR review</p>
            </div>
          </div>
        </div>

        <div class="preview-metrics">
          <div class="metric-card">
            <span>CV-JD Matching</span>
            <strong>Semantic Score</strong>
          </div>
          <div class="metric-card">
            <span>Skill Extraction</span>
            <div class="metric-tags">
              <b>Matched</b>
              <b>Missing</b>
            </div>
          </div>
          <div class="metric-card">
            <span>HR Screening</span>
            <strong>Bulk Ranking</strong>
          </div>
        </div>
      </div>
    </section>

    <section class="quick-actions">
      <router-link to="/jobseeker/analyze" class="quick-card">
        <span class="quick-icon">🎯</span>
        <div>
          <h3>CV-JD Analysis</h3>
          <p>Check match score, matched skills, and missing skills.</p>
        </div>
      </router-link>

      <router-link to="/jobseeker/search" class="quick-card">
        <span class="quick-icon">🔍</span>
        <div>
          <h3>Semantic Job Search</h3>
          <p>Find relevant jobs based on CV meaning, not only keywords.</p>
        </div>
      </router-link>

      <router-link to="/hr/rank" class="quick-card">
        <span class="quick-icon">📊</span>
        <div>
          <h3>Bulk CV Ranking</h3>
          <p>Upload multiple CVs and rank candidates automatically.</p>
        </div>
      </router-link>
    </section>

    <div class="feature-layout">
      <section class="feature-group glass-panel">
        <button class="accordion-header" type="button" @click="jobSeekerOpen = !jobSeekerOpen">
          <div>
            <span class="section-kicker">For Candidates</span>
            <h2>Job Seeker Features</h2>
          </div>
          <span class="accordion-icon">{{ jobSeekerOpen ? '−' : '+' }}</span>
        </button>

        <div class="accordion-content" v-show="jobSeekerOpen">
          <router-link to="/jobseeker/scrape" class="feature-card">
            <span class="feature-icon">🔎</span>
            <h3>Scrape & Find Matches</h3>
            <p>Find top job matches from LinkedIn based on your uploaded CV.</p>
          </router-link>

          <router-link to="/jobseeker/analyze" class="feature-card">
            <span class="feature-icon">📄</span>
            <h3>Detailed CV-JD Analysis</h3>
            <p>Compare CV content with a job description and identify skill gaps.</p>
          </router-link>

          <router-link to="/jobseeker/search" class="feature-card">
            <span class="feature-icon">✨</span>
            <h3>Semantic Job Search</h3>
            <p>Search jobs using semantic similarity so results are more contextual.</p>
          </router-link>
        </div>
      </section>

      <section class="feature-group glass-panel">
        <button class="accordion-header" type="button" @click="hrOpen = !hrOpen">
          <div>
            <span class="section-kicker">For Recruiters</span>
            <h2>HR Features</h2>
          </div>
          <span class="accordion-icon">{{ hrOpen ? '−' : '+' }}</span>
        </button>

        <div class="accordion-content" v-show="hrOpen">
          <router-link to="/hr/rank" class="feature-card">
            <span class="feature-icon">🏆</span>
            <h3>Bulk CV Ranking</h3>
            <p>Upload multiple CVs and rank candidates against one job description using hybrid semantic matching.</p>
          </router-link>

          <router-link to="/hr/talent-pool" class="feature-card">
            <span class="feature-icon">👥</span>
            <h3>Talent Pool Management</h3>
            <p>Store, track, and filter top-ranked candidates across different pipelines.</p>
          </router-link>

          <router-link to="/hr/interviews" class="feature-card">
            <span class="feature-icon">📅</span>
            <h3>AI Interview Scheduler</h3>
            <p>Generate tailored screening questions and schedule video interviews automatically.</p>
          </router-link>

          <router-link to="/hr-dashboard" class="feature-card">
            <span class="feature-icon">📊</span>
            <h3>HR Analytics Dashboard</h3>
            <p>Track recruitment conversion funnels, job category demands, top candidate skills, and daily activity logs.</p>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const jobSeekerOpen = ref(true)
const hrOpen = ref(true)
</script>

<style scoped>
.home-container {
  max-width: 1180px;
  margin: 0 auto;
}

.hero-section {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(380px, 0.95fr);
  gap: clamp(1.5rem, 4vw, 3.5rem);
  align-items: center;
  overflow: hidden;
  padding: clamp(2rem, 5vw, 4.3rem);
  margin-bottom: 1.4rem;
}

.hero-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 14% 16%, rgba(56, 189, 248, 0.16), transparent 32%),
    radial-gradient(circle at 82% 18%, rgba(99, 102, 241, 0.10), transparent 34%),
    radial-gradient(circle at 86% 82%, rgba(45, 212, 191, 0.12), transparent 34%),
    linear-gradient(135deg, rgba(255,255,255,0.42), rgba(255,255,255,0.16));
  pointer-events: none;
}

.hero-copy,
.workflow-preview {
  position: relative;
  z-index: 1;
}

.hero-badge,
.section-kicker,
.preview-kicker {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  border-radius: 999px;
  border: 1px solid rgba(14, 165, 233, 0.25);
  background: rgba(14, 165, 233, 0.12);
  color: var(--primary-dark);
  font-size: 0.82rem;
  font-weight: 800;
  padding: 0.42rem 0.75rem;
}

.badge-dot {
  width: 0.48rem;
  height: 0.48rem;
  margin-right: 0.45rem;
  border-radius: 999px;
  background: #22C55E;
  box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.15);
}

.hero-section h1 {
  max-width: 640px;
  margin: 1rem 0 1rem;
  font-size: clamp(2.4rem, 6vw, 5rem);
  line-height: 1;
  font-weight: 900;
  letter-spacing: -0.08em;
  color: var(--text);
}

.hero-section p {
  max-width: 620px;
  margin: 0;
  color: #475569;
  font-size: clamp(1rem, 2vw, 1.12rem);
  line-height: 1.75;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  margin-top: 1.65rem;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 52px;
  padding: 0.9rem 1.35rem;
  border-radius: 999px;
  font-weight: 850;
  text-decoration: none;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.hero-btn.primary {
  color: white;
  background: linear-gradient(135deg, var(--primary-dark), #0EA5E9 52%, #6366F1);
  box-shadow: 0 18px 38px rgba(14, 165, 233, 0.28);
}

.hero-btn.secondary {
  color: var(--primary-dark);
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(14, 165, 233, 0.24);
}

.hero-btn:hover {
  transform: translateY(-3px);
}

.workflow-preview {
  min-height: 475px;
  padding: 1.25rem;
  border-radius: 32px;
  background:
    linear-gradient(145deg, rgba(255,255,255,0.86), rgba(255,255,255,0.62)),
    radial-gradient(circle at 18% 18%, rgba(14,165,233,0.12), transparent 36%),
    radial-gradient(circle at 82% 86%, rgba(99,102,241,0.10), transparent 40%);
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.10);
  overflow: hidden;
  backdrop-filter: blur(18px);
}

.preview-glow {
  position: absolute;
  right: -80px;
  top: -90px;
  width: 260px;
  height: 260px;
  border-radius: 999px;
  background: rgba(14, 165, 233, 0.12);
  filter: blur(56px);
  pointer-events: none;
}

.preview-header {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.preview-kicker {
  padding: 0.32rem 0.6rem;
  font-size: 0.72rem;
}

.preview-header h2 {
  margin: 0.55rem 0 0;
  font-size: 1.25rem;
  color: #0F172A;
  background: none;
  -webkit-background-clip: initial;
  background-clip: initial;
}

.status-pill {
  border-radius: 999px;
  padding: 0.42rem 0.7rem;
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.22);
  color: #15803D;
  font-weight: 850;
  font-size: 0.78rem;
}

.workflow-steps {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 0.62rem;
}

.workflow-card {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.85rem;
  align-items: center;
  padding: 1rem;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.84);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.08);
}

.workflow-card.cv-card {
  margin-right: 2rem;
}

.workflow-card.analysis-card {
  margin-left: 2rem;
  background: linear-gradient(135deg, rgba(255,255,255,0.82), rgba(224,242,254,0.64));
}

.workflow-card.rank-card {
  margin-right: 1rem;
}

.step-number {
  position: absolute;
  right: 1rem;
  top: 0.8rem;
  color: rgba(3, 105, 161, 0.16);
  font-weight: 900;
  font-size: 1.35rem;
}

.step-icon,
.quick-icon,
.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.16), rgba(99, 102, 241, 0.15));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
}

.step-icon {
  width: 3.1rem;
  height: 3.1rem;
  font-size: 1.35rem;
}

.workflow-card h3 {
  margin: 0 0 0.25rem;
  color: #0F172A;
  font-size: 0.98rem;
}

.workflow-card p {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.45;
  color: #64748B;
}

.connector-line {
  width: 2px;
  height: 20px;
  margin-left: 2.55rem;
  background: linear-gradient(to bottom, rgba(14,165,233,0.12), rgba(99,102,241,0.42));
}

.preview-metrics {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.7rem;
  margin-top: 1rem;
}

.metric-card {
  min-height: 98px;
  padding: 0.9rem;
  border-radius: 20px;
  background: rgba(255,255,255,0.64);
  border: 1px solid rgba(255,255,255,0.78);
}

.metric-card span {
  display: block;
  margin-bottom: 0.45rem;
  color: #64748B;
  font-size: 0.76rem;
  font-weight: 800;
}

.metric-card strong {
  display: block;
  color: var(--primary-dark);
  font-size: 0.95rem;
  line-height: 1.35;
}

.metric-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.metric-tags b {
  border-radius: 999px;
  padding: 0.32rem 0.5rem;
  background: rgba(14, 165, 233, 0.12);
  color: var(--primary-dark);
  font-size: 0.7rem;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.35rem;
}

.quick-card {
  display: flex;
  gap: 0.9rem;
  align-items: flex-start;
  min-height: 142px;
  padding: 1.15rem;
  border-radius: 26px;
  color: inherit;
  text-decoration: none;
  background: rgba(255,255,255,0.64);
  border: 1px solid rgba(255,255,255,0.76);
  box-shadow: 0 16px 42px rgba(15,23,42,0.07);
  transition: transform 0.22s ease, box-shadow 0.22s ease, background 0.22s ease;
}

.quick-card:hover {
  transform: translateY(-5px);
  background: rgba(255,255,255,0.86);
  box-shadow: var(--shadow-sm);
}

.quick-icon {
  width: 3rem;
  height: 3rem;
  font-size: 1.25rem;
}

.quick-card h3 {
  margin: 0 0 0.45rem;
  color: var(--primary-dark);
  font-size: 1rem;
}

.quick-card p {
  margin: 0;
  color: #64748B;
  line-height: 1.55;
  font-size: 0.9rem;
}

.feature-layout {
  display: grid;
  gap: 1.2rem;
}

.feature-group {
  padding: 0;
  overflow: hidden;
}

.accordion-header {
  width: 100%;
  padding: 1.35rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  border: 0;
  cursor: pointer;
  text-align: left;
  background: rgba(255, 255, 255, 0.48);
  transition: background 0.3s ease;
}

.accordion-header:hover {
  background: rgba(255, 255, 255, 0.72);
}

.accordion-header h2 {
  margin: 0.55rem 0 0;
  font-size: 1.45rem;
}

.accordion-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 999px;
  background: rgba(14, 165, 233, 0.12);
  color: var(--primary-dark);
  font-size: 1.2rem;
  font-weight: 900;
}

.accordion-content {
  padding: 1.35rem;
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
}

.feature-card {
  display: block;
  min-height: 172px;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.82);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: inherit;
  transition: all 0.25s ease;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: var(--shadow-sm);
}

.feature-icon {
  width: 2.7rem;
  height: 2.7rem;
  margin-bottom: 0.9rem;
}

.feature-card h3 {
  color: var(--primary-dark);
  margin: 0 0 0.55rem;
  font-size: 1.08rem;
}

.feature-card p {
  color: #64748B;
  margin: 0;
  font-size: 0.94rem;
  line-height: 1.55;
}

@media (max-width: 980px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .workflow-preview {
    min-height: auto;
  }

  .quick-actions {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-section {
    padding: 1.45rem;
    border-radius: var(--radius-lg);
  }

  .hero-actions,
  .hero-btn {
    width: 100%;
  }

  .workflow-card.cv-card,
  .workflow-card.analysis-card,
  .workflow-card.rank-card {
    margin-left: 0;
    margin-right: 0;
  }

  .preview-header,
  .preview-metrics {
    grid-template-columns: 1fr;
  }

  .preview-metrics {
    display: grid;
  }

  .accordion-header,
  .accordion-content {
    padding: 1rem;
  }
}
</style>
