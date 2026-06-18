<template>
  <div class="landing-root">

    <!-- ===== HERO ===== -->
    <section class="hero-section">
      <div class="hero-inner">
        <div class="hero-badge">
          <span class="badge-pulse"></span>
          AI-Powered Career Platform
        </div>
        <h1 class="hero-title">
          Match Smarter.<br />
          <span class="gradient-text">Hire Faster.</span>
        </h1>
        <p class="hero-desc">
          HIREZY connects job seekers and HR professionals through AI-driven CV matching,
          real-time job scraping, and intelligent recruitment analytics — all in one platform.
        </p>
        <div class="hero-cta">
          <router-link to="/register" class="cta-btn cta-primary">
            Get Started Free
            <span class="cta-arrow">→</span>
          </router-link>
          <router-link to="/login" class="cta-btn cta-outline">
            Sign In
          </router-link>
        </div>
        <p class="hero-note">No credit card required. Free to use.</p>
      </div>

      <!-- Floating decorative cards -->
      <div class="hero-visual" aria-hidden="true">
        <div class="float-card fc-top glass-panel">
          <span class="fc-icon-sm">🎯</span>
          <div>
            <p class="fc-label">Match Score</p>
            <p class="fc-value">94%</p>
          </div>
        </div>
        <div class="float-card fc-mid glass-panel">
          <span class="fc-icon-sm">📄</span>
          <div>
            <p class="fc-label">CVs Analyzed</p>
            <p class="fc-value">12,400+</p>
          </div>
        </div>
        <div class="float-card fc-bot glass-panel">
          <span class="fc-icon-sm">🤖</span>
          <div>
            <p class="fc-label">AI Recommendations</p>
            <p class="fc-value">Powered by Gemini</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== FEATURES — JOB SEEKER ===== -->
    <section class="features-section">
      <div class="section-header">
        <span class="section-pill">For Job Seekers</span>
        <h2 class="section-title">Your AI Career Toolkit</h2>
        <p class="section-sub">Everything you need to land your dream job — powered by AI.</p>
      </div>

      <div class="features-grid">
        <div class="feat-card glass-panel">
          <div class="feat-icon-wrap feat-teal">📄</div>
          <h3>Check Resume</h3>
          <p>Upload your CV and a job description. Get an instant AI-powered match score, gap analysis, and actionable improvement tips.</p>
        </div>
        <div class="feat-card glass-panel">
          <div class="feat-icon-wrap feat-indigo">🔍</div>
          <h3>Job Scraper</h3>
          <p>Scrape real, live job listings from LinkedIn by keyword and location. Discover opportunities you'd never find manually.</p>
        </div>
        <div class="feat-card glass-panel feat-highlight">
          <div class="feat-icon-wrap feat-purple">🤖</div>
          <h3>AI Resume Advisor</h3>
          <p>Get a personalized learning roadmap, career growth suggestions, and resume optimization tips powered by Google Gemini.</p>
          <span class="feat-badge">Powered by Gemini</span>
        </div>
      </div>
    </section>

    <!-- ===== FEATURES — HR ===== -->
    <section class="features-section features-hr">
      <div class="section-header">
        <span class="section-pill section-pill-amber">For HR Recruiters</span>
        <h2 class="section-title">Smarter Recruitment, Faster Hiring</h2>
        <p class="section-sub">From CV screening to interview scheduling — automate the heavy lifting.</p>
      </div>

      <div class="features-grid">
        <div class="feat-card glass-panel">
          <div class="feat-icon-wrap feat-amber">📊</div>
          <h3>HR Analytics Dashboard</h3>
          <p>Track your full hiring pipeline: candidates, screening stages, interviews, and conversion rates in real-time.</p>
        </div>
        <div class="feat-card glass-panel">
          <div class="feat-icon-wrap feat-teal">🏆</div>
          <h3>Rank CV</h3>
          <p>Upload multiple CVs and let AI rank them by relevance to your job description. Save hours of manual screening.</p>
        </div>
        <div class="feat-card glass-panel">
          <div class="feat-icon-wrap feat-indigo">👥</div>
          <h3>Talent Pool</h3>
          <p>Save top-matching candidates to a talent pool. Filter and revisit promising profiles for future vacancies.</p>
        </div>
        <div class="feat-card glass-panel">
          <div class="feat-icon-wrap feat-green">📅</div>
          <h3>AI Interview Scheduler</h3>
          <p>Auto-generate smart screening questions and schedule video interviews — all without leaving the platform.</p>
        </div>
      </div>
    </section>

    <!-- ===== HOW IT WORKS ===== -->
    <section class="how-section">
      <div class="section-header">
        <span class="section-pill">Simple & Fast</span>
        <h2 class="section-title">How It Works</h2>
      </div>
      <div class="steps-row">
        <div class="step-card">
          <div class="step-num">01</div>
          <h4>Create Your Account</h4>
          <p>Sign up as a Job Seeker or HR Recruiter in seconds.</p>
        </div>
        <div class="step-connector" aria-hidden="true">→</div>
        <div class="step-card">
          <div class="step-num">02</div>
          <h4>Upload & Analyze</h4>
          <p>Upload your CV or job descriptions and let AI do the heavy lifting.</p>
        </div>
        <div class="step-connector" aria-hidden="true">→</div>
        <div class="step-card">
          <div class="step-num">03</div>
          <h4>Get AI Insights</h4>
          <p>Receive match scores, roadmaps, rankings, and actionable recommendations instantly.</p>
        </div>
        <div class="step-connector" aria-hidden="true">→</div>
        <div class="step-card">
          <div class="step-num">04</div>
          <h4>Take Action</h4>
          <p>Apply to the best jobs or hire the best candidates — confidently and efficiently.</p>
        </div>
      </div>
    </section>

    <!-- ===== FINAL CTA ===== -->
    <section class="final-cta glass-panel">
      <h2 class="cta-title">Ready to Transform Your Career or Hiring Process?</h2>
      <p class="cta-sub">Join thousands of job seekers and recruiters already using HIREZY.</p>
      <div class="hero-cta">
        <router-link to="/register" class="cta-btn cta-primary">
          Get Started — It's Free
          <span class="cta-arrow">→</span>
        </router-link>
        <router-link to="/login" class="cta-btn cta-outline">
          Sign In
        </router-link>
      </div>
    </section>

    <!-- ===== FOOTER ===== -->
    <footer class="landing-footer">
      <p>© 2026 HIREZY. AI-Powered Career Platform. Built for the future of work.</p>
    </footer>

  </div>
</template>

<script setup>
// Static landing page — no script needed
</script>

<style scoped>
/* ===========================
   ROOT & GLOBALS
=========================== */
.landing-root {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 1.5rem 4rem;
  display: flex;
  flex-direction: column;
  gap: 5rem;
}

/* ===========================
   HERO
=========================== */
.hero-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
  padding-top: 3.5rem;
}

.hero-inner {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(14, 165, 164, 0.08);
  border: 1px solid rgba(14, 165, 164, 0.2);
  border-radius: 999px;
  padding: 0.3rem 0.75rem;
  width: fit-content;
}

.badge-pulse {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: #22C55E;
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2);
  animation: pulse 2s ease infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2); }
  50%       { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0.05); }
}

.hero-title {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 900;
  line-height: 1.15;
  letter-spacing: -0.04em;
  color: var(--text);
  margin: 0;
}

.gradient-text {
  background: linear-gradient(135deg, var(--accent) 0%, var(--indigo) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-desc {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--text-muted);
  max-width: 480px;
  margin: 0;
}

.hero-cta {
  display: flex;
  gap: 0.9rem;
  flex-wrap: wrap;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: 700;
  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
}

.cta-primary {
  background: var(--accent);
  color: #fff;
  box-shadow: 0 4px 14px rgba(14, 165, 164, 0.3);
}
.cta-primary:hover {
  transform: translateY(-2px);
  filter: brightness(0.92);
  box-shadow: 0 8px 24px rgba(14, 165, 164, 0.4);
}

.cta-outline {
  background: transparent;
  color: var(--text-soft);
  border: 1.5px solid var(--border-strong);
}
.cta-outline:hover {
  transform: translateY(-2px);
  border-color: var(--accent);
  color: var(--accent);
}

.cta-arrow {
  transition: transform 0.18s ease;
}
.cta-btn:hover .cta-arrow { transform: translateX(3px); }

.hero-note {
  font-size: 0.78rem;
  color: var(--text-subtle);
  margin: 0;
}

/* Floating stat cards on the right */
.hero-visual {
  position: relative;
  height: 320px;
}

.float-card {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0.9rem 1.2rem;
  border-radius: var(--radius-md);
  min-width: 190px;
  animation: floatY 4s ease-in-out infinite;
}

.fc-top { top: 0; right: 10%; animation-delay: 0s; }
.fc-mid { top: 38%; left: 5%; animation-delay: 1.3s; }
.fc-bot { bottom: 0; right: 5%; animation-delay: 0.7s; }

@keyframes floatY {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-10px); }
}

.fc-icon-sm {
  font-size: 1.5rem;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(14,165,164,0.12), rgba(79,70,229,0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.fc-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0;
}

.fc-value {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text);
  margin: 0;
}

/* ===========================
   SECTION HEADER
=========================== */
.section-header {
  text-align: center;
  margin-bottom: 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
}

.section-pill {
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(14, 165, 164, 0.08);
  border: 1px solid rgba(14, 165, 164, 0.2);
  border-radius: 999px;
  padding: 0.25rem 0.75rem;
}
.section-pill-amber {
  color: var(--warning);
  background: rgba(217, 119, 6, 0.08);
  border-color: rgba(217, 119, 6, 0.2);
}

.section-title {
  font-size: clamp(1.4rem, 2.5vw, 1.9rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text);
  margin: 0;
}

.section-sub {
  font-size: 0.95rem;
  color: var(--text-muted);
  max-width: 520px;
  line-height: 1.6;
  margin: 0;
}

/* ===========================
   FEATURE CARDS
=========================== */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.features-hr .features-grid {
  grid-template-columns: repeat(4, 1fr);
}

.feat-card {
  padding: 1.75rem 1.5rem;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  position: relative;
}

.feat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.feat-card h3 {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text);
  margin: 0;
}

.feat-card p {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--text-muted);
  margin: 0;
}

.feat-highlight {
  border-color: rgba(124, 58, 237, 0.25) !important;
}
.feat-highlight:hover {
  border-color: var(--purple) !important;
}

.feat-badge {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--purple);
  background: rgba(124, 58, 237, 0.08);
  border: 1px solid rgba(124, 58, 237, 0.2);
  border-radius: 999px;
  padding: 0.2rem 0.6rem;
  width: fit-content;
}

/* Icon wraps */
.feat-icon-wrap {
  width: 2.8rem;
  height: 2.8rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
}
.feat-teal   { background: rgba(14,165,164,0.1);  border: 1px solid rgba(14,165,164,0.2); }
.feat-indigo { background: rgba(79,70,229,0.1);   border: 1px solid rgba(79,70,229,0.2); }
.feat-purple { background: rgba(124,58,237,0.1);  border: 1px solid rgba(124,58,237,0.2); }
.feat-amber  { background: rgba(217,119,6,0.1);   border: 1px solid rgba(217,119,6,0.2); }
.feat-green  { background: rgba(22,163,74,0.1);   border: 1px solid rgba(22,163,74,0.2); }

/* ===========================
   HOW IT WORKS
=========================== */
.how-section {
  /* no extra styles needed */
}

.steps-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.step-card {
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.75rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  box-shadow: var(--shadow-xs);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.step-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.step-num {
  font-size: 2rem;
  font-weight: 900;
  color: var(--accent);
  opacity: 0.25;
  line-height: 1;
}

.step-card h4 {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text);
  margin: 0;
}

.step-card p {
  font-size: 0.84rem;
  line-height: 1.55;
  color: var(--text-muted);
  margin: 0;
}

.step-connector {
  font-size: 1.5rem;
  color: var(--border-strong);
  flex-shrink: 0;
  padding: 0 0.25rem;
}

/* ===========================
   FINAL CTA
=========================== */
.final-cta {
  text-align: center;
  padding: 3.5rem 2rem;
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, rgba(14,165,164,0.05) 0%, rgba(79,70,229,0.05) 100%) !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.cta-title {
  font-size: clamp(1.3rem, 2.5vw, 1.8rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text);
  max-width: 560px;
  line-height: 1.3;
  margin: 0;
}

.cta-sub {
  font-size: 0.95rem;
  color: var(--text-muted);
  margin: 0;
}

/* ===========================
   FOOTER
=========================== */
.landing-footer {
  text-align: center;
  padding: 1.5rem 0 0;
  border-top: 1px solid var(--border);
  font-size: 0.8rem;
  color: var(--text-subtle);
  margin-top: -3rem;
}

/* ===========================
   RESPONSIVE
=========================== */
@media (max-width: 1024px) {
  .features-hr .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
    padding-top: 2rem;
    gap: 2rem;
  }
  .hero-desc { max-width: 100%; }
  .hero-cta  { justify-content: center; }
  .hero-note { text-align: center; }
  .hero-visual { display: none; }

  .features-grid {
    grid-template-columns: 1fr;
  }
  .features-hr .features-grid {
    grid-template-columns: 1fr;
  }

  .steps-row {
    flex-direction: column;
    gap: 1rem;
  }
  .step-connector {
    transform: rotate(90deg);
    font-size: 1.2rem;
  }
  .step-card { width: 100%; }

  .landing-root { gap: 3.5rem; }
}

@media (max-width: 580px) {
  .landing-root { padding: 0 1rem 3rem; }
  .hero-cta {
    flex-direction: column;
    align-items: stretch;
  }
  .cta-btn {
    justify-content: center;
  }
  .final-cta { padding: 2.5rem 1.2rem; }
}
</style>
