<template>
  <div class="app-container">
    <Toast ref="toast" />

    <div class="bg-gradient-mesh" aria-hidden="true">
      <span class="mesh-sphere sphere-1"></span>
      <span class="mesh-sphere sphere-2"></span>
      <span class="mesh-sphere sphere-3"></span>
      <span class="mesh-grid"></span>
    </div>

    <nav class="navbar">
      <div class="nav-inner">
        <router-link to="/" class="nav-brand" @click="closeMenus">
          <img class="brand-icon" src="/icon.svg" alt="CV Matcher Pro logo" />
          <span class="brand-text">CV Matcher Pro</span>
        </router-link>

        <button
          class="menu-toggle"
          :class="{ 'is-open': isMobileMenuOpen }"
          type="button"
          aria-label="Toggle navigation menu"
          :aria-expanded="isMobileMenuOpen"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <div class="nav-links" :class="{ 'is-open': isMobileMenuOpen }">
          <router-link
            to="/"
            class="nav-link"
            exact-active-class="is-active"
            @click="closeMenus"
          >
            Home
          </router-link>

          <div class="dropdown" :class="{ 'is-open': openDropdown === 'jobseeker' }">
            <button
              class="dropdown-btn"
              :class="{ 'is-active': isJobSeekerActive }"
              type="button"
              @click="toggleDropdown('jobseeker')"
            >
              <span>Job Seeker</span>
              <span class="arrow">▾</span>
            </button>
            <div class="dropdown-content">
              <router-link to="/jobseeker/scrape" active-class="is-active" @click="closeMenus">
                Scrape Jobs
              </router-link>
              <router-link to="/jobseeker/analyze" active-class="is-active" @click="closeMenus">
                CV-JD Analysis
              </router-link>
              <router-link to="/jobseeker/search" active-class="is-active" @click="closeMenus">
                Semantic Search
              </router-link>
            </div>
          </div>

          <div class="dropdown" :class="{ 'is-open': openDropdown === 'hr' }">
            <button
              class="dropdown-btn"
              :class="{ 'is-active': isHrActive }"
              type="button"
              @click="toggleDropdown('hr')"
            >
              <span>HR Panel</span>
              <span class="arrow">▾</span>
            </button>
            <div class="dropdown-content">
              <router-link to="/hr/rank" active-class="is-active" @click="closeMenus">
                Bulk CV Ranking
              </router-link>
              <router-link to="/hr/cluster" active-class="is-active" @click="closeMenus">
                Talent Clustering
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Toast from './components/Toast.vue'

const toast = ref(null)
const route = useRoute()
const isMobileMenuOpen = ref(false)
const openDropdown = ref(null)

const isJobSeekerActive = computed(() => route.path.startsWith('/jobseeker'))
const isHrActive = computed(() => route.path.startsWith('/hr'))
const currentPageTitle = computed(() => {
  const appName = 'CV Matcher Pro'
  return route.meta?.title ? `${route.meta.title} | ${appName}` : appName
})

function toggleDropdown(name) {
  openDropdown.value = openDropdown.value === name ? null : name
}

function closeMenus() {
  isMobileMenuOpen.value = false
  openDropdown.value = null
}

watch(currentPageTitle, (title) => {
  document.title = title
}, { immediate: true })

watch(() => route.fullPath, closeMenus)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

:root {
  --primary: #0284c7;
  --primary-dark: #075985;
  --primary-soft: #e0f2fe;
  --accent: #22d3ee;
  --accent-2: #6366f1;
  --success: #10b981;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --secondary: #0EA5E9;
  --indigo: #6366F1;
  --purple: #8B5CF6;
  --success: #22C55E;
  --danger: #EF4444;
  --warning: #F59E0B;
  --text: #0F172A;
  --text-soft: #1E3A5F;
  --text-muted: #64748B;
  --surface: rgba(255, 255, 255, 0.72);
  --surface-strong: rgba(255, 255, 255, 0.9);
  --glass-bg: rgba(255, 255, 255, 0.62);
  --glass-border: rgba(255, 255, 255, 0.7);
  --line: rgba(14, 116, 144, 0.14);
  --shadow-soft: 0 20px 60px rgba(15, 23, 42, 0.08);
  --shadow-strong: 0 24px 70px rgba(3, 105, 161, 0.18);
  --blur-amount: 22px;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--text);
  min-height: 100vh;
  background:
    radial-gradient(circle at 12% 18%, rgba(56, 189, 248, 0.14), transparent 30%),
    radial-gradient(circle at 78% 22%, rgba(99, 102, 241, 0.10), transparent 32%),
    radial-gradient(circle at 88% 78%, rgba(45, 212, 191, 0.12), transparent 34%),
    linear-gradient(135deg, #f8fcff 0%, #eef8ff 48%, #f8f5ff 100%);
  position: relative;
  overflow-x: hidden;
}

button,
input,
select,
textarea {
  font: inherit;
}

.app-container {
  min-height: 100vh;
  position: relative;
  isolation: isolate;
}

.bg-gradient-mesh {
  position: fixed;
  inset: 0;
  z-index: -2;
  overflow: hidden;
  pointer-events: none;
}

.mesh-sphere {
  position: absolute;
  border-radius: 999px;
  filter: blur(110px);
  opacity: 0.34;
  animation: float 22s infinite ease-in-out;
}

.sphere-1 {
  top: -18%;
  left: -14%;
  width: min(520px, 50vw);
  height: min(520px, 50vw);
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.42), rgba(99, 102, 241, 0.24));
}

.sphere-2 {
  right: -16%;
  top: 24%;
  width: min(560px, 54vw);
  height: min(560px, 54vw);
  background: linear-gradient(135deg, rgba(45, 212, 191, 0.26), rgba(14, 165, 233, 0.24));
  animation-delay: -7s;
}

.sphere-3 {
  left: 40%;
  bottom: -24%;
  width: min(480px, 48vw);
  height: min(480px, 48vw);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.18), rgba(14, 165, 233, 0.12));
  animation-delay: -13s;
}

.mesh-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(3, 105, 161, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(3, 105, 161, 0.035) 1px, transparent 1px);
  background-size: 46px 46px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.56), transparent 76%);
}

@keyframes float {
  0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
  50% { transform: translate3d(22px, 42px, 0) scale(1.12); }
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  margin: 0;
  border-inline: none;
  text-align: left;
}

.navbar {
  width: 100%;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border-bottom: 1px solid rgba(255, 255, 255, 0.72);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 12px 38px rgba(15, 23, 42, 0.06);
}

.nav-inner {
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  padding: 0.8rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.nav-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.72rem;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-icon {
  width: 2.45rem;
  height: 2.45rem;
  display: block;
  filter: drop-shadow(0 10px 18px rgba(3, 105, 161, 0.24)); 
}

.brand-text {
  background: linear-gradient(135deg, var(--primary-dark), var(--secondary), var(--indigo));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-size: 1.12rem;
  font-weight: 800;
  letter-spacing: -0.4px;
  white-space: nowrap;
}

.nav-links {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.55rem;
}

.nav-link,
.dropdown-btn {
  position: relative;
  color: var(--text-soft);
  text-decoration: none;
  font-weight: 800;
  font-size: 0.94rem;
  padding: 0.68rem 1rem;
  border-radius: 999px;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, color 0.18s ease;
}

.nav-link:hover,
.dropdown-btn:hover,
.nav-link.is-active,
.dropdown-btn.is-active,
.dropdown.is-open .dropdown-btn {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.16), rgba(99, 102, 241, 0.14));
  color: var(--primary-dark);
  box-shadow: inset 0 0 0 1px rgba(14, 165, 233, 0.15), 0 10px 24px rgba(3, 105, 161, 0.09);
}

.nav-link:hover,
.dropdown-btn:hover {
  transform: translateY(-1px);
}

.nav-link.is-active::after,
.dropdown-btn.is-active::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 0.35rem;
  width: 20px;
  height: 3px;
  border-radius: 999px;
  transform: translateX(-50%);
  background: linear-gradient(90deg, var(--secondary), var(--indigo));
}

.dropdown {
  position: relative;
}

.dropdown-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
}

.arrow {
  font-size: 0.75rem;
  transition: transform 0.2s ease;
}

.dropdown:hover .arrow,
.dropdown.is-open .arrow,
.dropdown-btn.is-active .arrow {
  transform: rotate(180deg);
}

.dropdown-content {
  display: none;
  position: absolute;
  top: calc(100% + 0.65rem);
  left: 0;
  min-width: 238px;
  padding: 0.45rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.93);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border: 1px solid rgba(255, 255, 255, 0.84);
  box-shadow: 0 22px 55px rgba(15, 23, 42, 0.12);
  z-index: 1100;
}

.dropdown:hover .dropdown-content,
.dropdown.is-open .dropdown-content {
  display: block;
}

.dropdown-content a {
  display: block;
  padding: 0.82rem 0.95rem;
  color: var(--text-soft);
  text-decoration: none;
  font-weight: 700;
  border-radius: 14px;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.dropdown-content a:hover,
.dropdown-content a.is-active,
.dropdown-content a.router-link-active {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.14), rgba(99, 102, 241, 0.12));
  color: var(--primary-dark);
  transform: translateX(2px);
}

.menu-toggle {
  display: none;
  width: 2.65rem;
  height: 2.65rem;
  border: 1px solid rgba(14, 165, 233, 0.18);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 10px 24px rgba(3, 105, 161, 0.08);
  cursor: pointer;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 0.28rem;
}

.menu-toggle span {
  width: 1.15rem;
  height: 2px;
  border-radius: 999px;
  background: var(--primary-dark);
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.menu-toggle.is-open span:nth-child(1) {
  transform: translateY(6px) rotate(45deg);
}

.menu-toggle.is-open span:nth-child(2) {
  opacity: 0;
}

.menu-toggle.is-open span:nth-child(3) {
  transform: translateY(-6px) rotate(-45deg);
}

.main-content {
  flex: 1;
  padding: 2.7rem 2rem;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
}

.glass-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border: 1px solid var(--glass-border);
  border-radius: 28px;
  box-shadow: var(--shadow-soft);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.glass-panel:hover {
  box-shadow: var(--shadow-strong);
  border-color: rgba(255, 255, 255, 0.9);
}

.view-container {
  margin: 0 auto;
  padding: 2.8rem;
  max-width: 1200px;
}

h1,
h2,
h3,
h4 {
  color: var(--text);
  letter-spacing: -0.03em;
}

h2 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-weight: 800;
  font-size: clamp(1.65rem, 3vw, 2.25rem);
  background: linear-gradient(135deg, var(--primary-dark), var(--secondary), var(--indigo));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.subtitle {
  color: var(--text-muted);
  font-size: 1.03rem;
  margin: 0 0 2.4rem;
  line-height: 1.7;
}

.form-group {
  margin-bottom: 1.55rem;
}

label {
  display: block;
  font-weight: 800;
  margin-bottom: 0.65rem;
  font-size: 0.94rem;
  color: var(--text-soft);
}

.input-field {
  width: 100%;
  padding: 0.95rem 1.08rem;
  border: 1px solid rgba(14, 116, 144, 0.18);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
  font-size: 0.98rem;
  color: var(--text);
  transition: all 0.2s ease;
}

.input-field:hover {
  border-color: rgba(14, 165, 233, 0.36);
  background: rgba(255, 255, 255, 0.92);
}

.input-field:focus {
  outline: none;
  border-color: rgba(14, 165, 233, 0.8);
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.95);
  background: #FFFFFF;
}

.textarea {
  min-height: 150px;
  resize: vertical;
}

.file-input {
  cursor: pointer;
}

.btn-primary,
.btn-danger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 48px;
  padding: 0.88rem 1.35rem;
  border: none;
  border-radius: 999px;
  color: #FFFFFF;
  font-size: 0.98rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease, filter 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary) 48%, var(--indigo) 100%);
  box-shadow: 0 16px 34px rgba(14, 165, 233, 0.28);
}

.btn-danger {
  background: linear-gradient(135deg, #DC2626 0%, #EF4444 52%, #F97316 100%);
  box-shadow: 0 16px 34px rgba(239, 68, 68, 0.24);
}

.btn-primary:hover:not(:disabled),
.btn-danger:hover:not(:disabled) {
  transform: translateY(-2px);
  filter: saturate(1.08);
}

.btn-primary:active:not(:disabled),
.btn-danger:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled,
.btn-danger:disabled {
  cursor: not-allowed;
  opacity: 0.56;
  box-shadow: none;
  filter: grayscale(0.2);
}

.results {
  margin-top: 2.2rem;
}

.table-container {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.78);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
}

.skills-grid {
  display: grid;
  gap: 1.15rem;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.skills-card {
  padding: 1.25rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.64);
  border: 1px solid rgba(255, 255, 255, 0.76);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
}

.skills-card h4 {
  margin: 0 0 0.85rem;
  font-weight: 800;
  color: var(--text-soft);
}

@media (max-width: 768px) {
  .nav-inner {
    padding: 0.78rem 1rem;
    flex-wrap: wrap;
  }

  .brand-icon {
    width: 2.2rem;
    height: 2.2rem;
  }

  .brand-text {
    font-size: 1rem;
  }

  .menu-toggle {
    display: inline-flex;
  }

  .nav-links {
    display: none;
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    gap: 0.5rem;
    padding-top: 0.75rem;
  }

  .nav-links.is-open {
    display: flex;
  }

  .nav-link,
  .dropdown-btn {
    width: 100%;
    justify-content: space-between;
    padding: 0.9rem 1rem;
    background: rgba(255, 255, 255, 0.48);
    border-radius: 16px;
  }

  .nav-link.is-active::after,
  .dropdown-btn.is-active::after {
    left: 1rem;
    bottom: 0.42rem;
    transform: none;
  }

  .dropdown {
    width: 100%;
  }

  .dropdown-content {
    position: static;
    width: 100%;
    min-width: 0;
    margin-top: 0.4rem;
    padding: 0.4rem;
    box-shadow: none;
    background: rgba(255, 255, 255, 0.52);
  }

  .dropdown:hover .dropdown-content {
    display: none;
  }

  .dropdown.is-open .dropdown-content {
    display: block;
  }

  .dropdown-content a {
    white-space: normal;
  }

  .main-content {
    padding: 1.35rem 1rem 2rem;
  }

  .view-container {
    padding: 1.5rem;
    border-radius: 22px;
  }
}

@media (max-width: 420px) {
  .brand-text {
    max-width: 178px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .btn-primary,
  .btn-danger {
    width: 100%;
  }
}
</style>
