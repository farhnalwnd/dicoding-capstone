<template>
  <div class="app-container">
    <ToastNotification ref="toast" />



    <nav v-if="showNavbar" class="navbar">
      <div class="nav-inner">
        <!-- Brand -->
        <router-link to="/" class="nav-brand" @click="closeMenus">
          <img class="brand-icon" src="/hirezy-logo.png" alt="HIREZY logo" />
          <span class="brand-text">HIREZY</span>
        </router-link>

        <!-- Hamburger for mobile -->
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

          <!-- === JOB SEEKER flat links === -->
          <template v-if="isLoggedIn && isJobSeekerRole">
            <router-link
              to="/jobseeker/analyze"
              class="nav-link"
              active-class="is-active"
              @click="closeMenus"
            >Check Resume</router-link>
            <router-link
              to="/jobseeker/scrape"
              class="nav-link"
              active-class="is-active"
              @click="closeMenus"
            >Job Scraper</router-link>
            <router-link
              to="/resume-advisor"
              class="nav-link"
              active-class="is-active"
              @click="closeMenus"
            >AI Resume Advisor</router-link>
          </template>

          <!-- === HR flat links === -->
          <template v-if="isLoggedIn && isHr">
            <router-link
              to="/hr-dashboard"
              class="nav-link"
              active-class="is-active"
              @click="closeMenus"
            >HR Analytics</router-link>
            <router-link
              to="/hr/rank-cv"
              class="nav-link"
              active-class="is-active"
              @click="closeMenus"
            >Rank CV</router-link>
            <router-link
              to="/hr/talent-pool"
              class="nav-link"
              active-class="is-active"
              @click="closeMenus"
            >Talent Pool</router-link>
            <router-link
              to="/hr/interviews"
              class="nav-link"
              active-class="is-active"
              @click="closeMenus"
            >Interview Scheduler</router-link>
          </template>

          <!-- === Admin dropdown (keep as dropdown — more items) === -->
          <div v-if="isLoggedIn && isAdminRole" class="dropdown" :class="{ 'is-open': openDropdown === 'admin' }">
            <button
              class="dropdown-btn admin-dropdown-btn"
              type="button"
              @click="toggleDropdown('admin')"
            >
              <span>Admin Panel</span>
              <span class="arrow">▾</span>
            </button>
            <div class="dropdown-content">
              <router-link to="/admin" active-class="is-active" @click="closeMenus">Overview</router-link>
              <router-link to="/admin/users" active-class="is-active" @click="closeMenus">User Management</router-link>
            </div>
          </div>

          <!-- Spacer -->
          <div class="nav-spacer"></div>

          <!-- Theme Toggle -->
          <button
            class="theme-toggle-btn"
            type="button"
            @click="toggleTheme"
            aria-label="Toggle Dark Mode"
          >{{ isDarkMode ? '🌙' : '☀️' }}</button>

          <!-- Guest buttons -->
          <router-link
            v-if="!isLoggedIn"
            to="/login"
            class="nav-link nav-btn-login"
            @click="closeMenus"
          >Login</router-link>
          <router-link
            v-if="!isLoggedIn"
            to="/register"
            class="nav-btn-register"
            @click="closeMenus"
          >Register</router-link>

          <!-- User avatar dropdown -->
          <div v-if="isLoggedIn" class="dropdown user-dropdown" :class="{ 'is-open': openDropdown === 'user' }">
            <button
              class="dropdown-btn user-profile-btn"
              type="button"
              @click="toggleDropdown('user')"
            >
              <div class="nav-avatar">{{ userInitial }}</div>
              <span class="nav-username">{{ userName }}</span>
              <span class="arrow">▾</span>
            </button>
            <div class="dropdown-content user-dropdown-content">
              <div class="user-info-header">
                <p class="header-name">{{ userName }}</p>
                <p class="header-role">{{ isHr ? 'HR Recruiter' : isJobSeekerRole ? 'Job Seeker' : 'Admin' }}</p>
              </div>
              <button class="dropdown-logout-btn" @click="handleLogout">
                <span class="logout-icon">🚪</span> Logout
              </button>
            </div>
          </div>

        </div>
      </div>
    </nav>

    <main class="main-content" :class="{ 'landing-main': isLandingPage }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch, provide, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ToastNotification from './components/ToastNotification.vue'
import { authState, isAuthenticated, isHR, isJobSeeker, isAdmin, logout } from './stores/auth'

const toast = ref(null)
provide('toast', {
  show: (msg, opts) => toast.value?.show(msg, opts),
  hide: () => toast.value?.hide(),
  success: (msg) => toast.value?.show(msg, { type: 'success' }),
  error: (msg) => toast.value?.show(msg, { type: 'error' }),
  warning: (msg) => toast.value?.show(msg, { type: 'warning' }),
  info: (msg) => toast.value?.show(msg, { type: 'info' })
})
const route  = useRoute()
const router = useRouter()
const isMobileMenuOpen = ref(false)
const openDropdown = ref(null)

const isJobSeekerActive = computed(() => route.path.startsWith('/jobseeker'))
const isHrActive = computed(() => route.path.startsWith('/hr'))
const currentPageTitle = computed(() => {
  const appName = 'HIREZY'
  return route.meta?.title ? `${route.meta.title} | ${appName}` : appName
})

const isLoggedIn = computed(() => isAuthenticated.value)
const isHr = computed(() => isHR.value)
const isJobSeekerRole = computed(() => isJobSeeker.value)
const isAdminRole = computed(() => isAdmin.value)
const userName = computed(() => authState.user?.name || 'User')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())

const showNavbar = computed(() => {
  return route.path !== '/login' && route.path !== '/register'
})

const isLandingPage = computed(() => route.path === '/')

function handleLogout() {
  closeMenus()
  logout()
  router.push('/login')
}

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

const isDarkMode = ref(false)

function toggleTheme() {
  isDarkMode.value = !isDarkMode.value
  const theme = isDarkMode.value ? 'dark' : 'light'
  localStorage.setItem('theme', theme)
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDarkMode.value = true
    document.documentElement.classList.add('dark')
  }
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* =============================================================
   DESIGN SYSTEM — HIREZY  (Enterprise Edition)
   Inspired by: Ashby, Linear, Stripe Dashboard, Notion
   ============================================================= */

:root {
  /* Brand */
  --primary:        #0F172A;
  --primary-dark:   #1E293B;
  --secondary:      #334155;
  --accent:         #0EA5A4;
  --accent-light:   #CCFBF1;
  --indigo:         #4F46E5;
  --purple:         #7C3AED;

  /* Semantic */
  --success:        #16A34A;
  --success-bg:     #F0FDF4;
  --warning:        #D97706;
  --warning-bg:     #FFFBEB;
  --danger:         #DC2626;
  --danger-bg:      #FEF2F2;
  --info:           #0284C7;
  --info-bg:        #EFF6FF;

  /* Neutrals */
  --bg:             #F8FAFC;
  --surface:        #FFFFFF;
  --surface-2:      #F1F5F9;
  --border:         #E2E8F0;
  --border-strong:  #CBD5E1;

  /* Text */
  --text:           #0F172A;
  --text-soft:      #1E293B;
  --text-muted:     #64748B;
  --text-subtle:    #94A3B8;

  /* Shadows — 2-level system */
  --shadow-xs:    0 1px 2px rgba(0,0,0,0.05);
  --shadow-sm:    0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04);
  --shadow-md:    0 4px 6px rgba(0,0,0,0.07), 0 10px 30px rgba(0,0,0,0.06);
  --shadow-lg:    0 8px 16px rgba(0,0,0,0.08), 0 24px 48px rgba(0,0,0,0.07);
  --shadow-soft:  var(--shadow-sm);
  --shadow-strong:var(--shadow-md);

  /* Radii */
  --radius-xs:   6px;
  --radius-sm:   8px;
  --radius-md:   12px;
  --radius-lg:   16px;
  --radius-xl:   20px;
  --radius-full: 999px;

  /* Compat aliases (glassmorphism → solid) */
  --glass-bg:     var(--surface);
  --glass-border: var(--border);
  --blur-amount:  0px;
  --line:         #E2E8F0;
}

:root.dark {
  /* Brand override */
  --primary:        #F8FAFC;
  --primary-dark:   #F1F5F9;
  --secondary:      #CBD5E1;
  
  /* Neutrals inverted */
  --bg:             #0F172A;
  --surface:        #1E293B;
  --surface-2:      #334155;
  --border:         #334155;
  --border-strong:  #475569;

  /* Text inverted */
  --text:           #F8FAFC;
  --text-soft:      #F1F5F9;
  --text-muted:     #94A3B8;
  --text-subtle:    #64748B;
  
  /* Misc */
  --line:           #334155;
  --glass-bg:       var(--surface);
  --glass-border:   var(--border);
}

/* =============================================================  SCROLLBAR  ============================================================= */
::-webkit-scrollbar          { width: 5px; height: 5px; }
::-webkit-scrollbar-track    { background: transparent; }
::-webkit-scrollbar-thumb    { background: #CBD5E1; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }
*                            { scrollbar-width: thin; scrollbar-color: #CBD5E1 transparent; }

/* =============================================================  BASE  ============================================================= */
* { box-sizing: border-box; }

.theme-toggle-btn {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  color: var(--text);
}
.theme-toggle-btn:hover {
  background-color: var(--surface-2);
}

body {
  margin: 0; padding: 0;
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
  font-size: 15px; line-height: 1.6;
  color: var(--text);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

button, input, select, textarea { font: inherit; }

/* =============================================================  TYPOGRAPHY  ============================================================= */
h1, h2, h3, h4, h5, h6 {
  color: var(--text);
  letter-spacing: -0.025em;
  font-weight: 700;
  margin: 0;
}
h1 { font-size: clamp(1.4rem, 3vw, 1.9rem); line-height: 1.2; }
h2 { font-size: clamp(1.1rem, 2.5vw, 1.4rem); line-height: 1.3; color: var(--text); font-weight: 700; }
h3 { font-size: 1rem; font-weight: 700; }
h4 { font-size: 0.875rem; font-weight: 600; }
p  { margin: 0; }

/* Only for hero/highlight use */
.heading-gradient {
  background: linear-gradient(135deg, var(--accent) 0%, var(--indigo) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* =============================================================  APP SHELL  ============================================================= */
#app {
  display: flex; flex-direction: column;
  min-height: 100vh; width: 100%; max-width: 100%;
  margin: 0; text-align: left;
}
.app-container { min-height: 100vh; position: relative; }

/* =============================================================  NAVBAR  ============================================================= */
.navbar {
  width: 100%;
  background: #FFFFFF;
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 1000;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.nav-inner {
  width: 100%; max-width: 1280px; margin: 0 auto;
  padding: 0 1.5rem; height: 54px;
  display: flex; align-items: center;
  justify-content: space-between; gap: 1rem;
}

.nav-brand {
  display: inline-flex; align-items: center; gap: 0.6rem;
  text-decoration: none; flex-shrink: 0;
}

.brand-icon { width: 1.85rem; height: 1.85rem; display: block; }

.brand-text {
  color: var(--primary);
  font-size: 0.95rem; font-weight: 700;
  letter-spacing: -0.03em; white-space: nowrap;
}

.nav-links {
  display: flex; align-items: center;
  justify-content: flex-end; gap: 0.15rem;
  flex: 1;
}

.nav-spacer { flex: 1; }

.nav-link,
.dropdown-btn {
  position: relative;
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500; font-size: 0.875rem;
  padding: 0.45rem 0.8rem;
  border-radius: var(--radius-sm);
  transition: background 0.15s ease, color 0.15s ease;
}

.nav-link:hover,
.dropdown-btn:hover,
.dropdown.is-open .dropdown-btn {
  background: var(--surface-2);
  color: var(--primary);
}

.nav-link.is-active,
.dropdown-btn.is-active {
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 600;
}

.nav-link.is-active::after,
.dropdown-btn.is-active::after { display: none; }

.dropdown { position: relative; }

.dropdown-btn {
  background: transparent; border: none; cursor: pointer;
  display: inline-flex; align-items: center; gap: 0.3rem;
}

/* Admin accent */
.admin-dropdown-btn { color: var(--danger) !important; }
.admin-dropdown-btn:hover,
.dropdown.is-open .admin-dropdown-btn {
  background: var(--danger-bg) !important;
  color: #B91C1C !important;
}

.arrow {
  font-size: 0.6rem; color: var(--text-subtle);
  transition: transform 0.18s ease;
}

.dropdown:hover .arrow,
.dropdown.is-open .arrow { transform: rotate(180deg); }

.dropdown-content {
  display: none;
  position: absolute; top: calc(100% + 5px); left: 0;
  min-width: 200px; padding: 4px;
  border-radius: var(--radius-md);
  background: #FFFFFF;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-lg);
  z-index: 1100;
}

.dropdown:hover .dropdown-content,
.dropdown.is-open .dropdown-content { display: block; }

.dropdown-content a {
  display: block; padding: 0.5rem 0.8rem;
  color: var(--text-soft);
  text-decoration: none; font-weight: 500;
  font-size: 0.875rem; border-radius: var(--radius-xs);
  transition: background 0.12s ease, color 0.12s ease;
  white-space: nowrap;
}

.dropdown-content a:hover,
.dropdown-content a.is-active,
.dropdown-content a.router-link-active {
  background: var(--surface-2); color: var(--primary); font-weight: 600;
}

/* =============================================================  MENU TOGGLE  ============================================================= */
.menu-toggle {
  display: none;
  width: 2.1rem; height: 2.1rem;
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--surface); cursor: pointer;
  align-items: center; justify-content: center;
  flex-direction: column; gap: 0.22rem;
}
.menu-toggle span {
  width: 0.95rem; height: 1.5px; border-radius: 999px;
  background: var(--text-soft);
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.menu-toggle.is-open span:nth-child(1) { transform: translateY(5px) rotate(45deg); }
.menu-toggle.is-open span:nth-child(2) { opacity: 0; }
.menu-toggle.is-open span:nth-child(3) { transform: translateY(-5px) rotate(-45deg); }

/* =============================================================  LAYOUT  ============================================================= */
.main-content {
  flex: 1; padding: 2rem 1.5rem;
  max-width: 1280px; margin: 0 auto; width: 100%;
}
.landing-main {
  padding-left: 0; padding-right: 0; max-width: 100%;
}
.view-container { margin: 0 auto; padding: 2rem; max-width: 1200px; }

/* =============================================================  CARD SYSTEM  ============================================================= */
.glass-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
.glass-panel:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-strong);
}

/* =============================================================  FORMS  ============================================================= */
.form-group { margin-bottom: 1.1rem; }

label {
  display: block;
  font-weight: 600; font-size: 0.8rem;
  color: var(--text-soft); margin-bottom: 0.35rem;
}

.input-field {
  width: 100%; padding: 0.6rem 0.85rem;
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--surface); font-size: 0.875rem;
  color: var(--text);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  appearance: none; -webkit-appearance: none;
}
.input-field::placeholder { color: var(--text-subtle); }
.input-field:hover { border-color: var(--border-strong); }
.input-field:focus {
  outline: none; border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(14,165,164,0.12);
}

select.input-field {
  padding-right: 2.25rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 0.75rem center;
  cursor: pointer;
}

.textarea { min-height: 130px; resize: vertical; line-height: 1.6; }

/* =============================================================  BUTTONS  ============================================================= */
.btn-primary,
.btn-danger {
  display: inline-flex; align-items: center;
  justify-content: center; gap: 0.4rem;
  min-height: 36px; padding: 0.5rem 1rem;
  border: none; border-radius: var(--radius-sm);
  color: #FFFFFF; font-size: 0.875rem; font-weight: 600;
  cursor: pointer; white-space: nowrap;
  transition: filter 0.15s ease, transform 0.12s ease, box-shadow 0.15s ease;
}

.btn-primary {
  background: var(--accent);
  box-shadow: 0 1px 2px rgba(14,165,164,0.2);
}
.btn-danger {
  background: var(--danger);
  box-shadow: 0 1px 2px rgba(220,38,38,0.18);
}
.btn-primary:hover:not(:disabled) {
  filter: brightness(0.9); transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(14,165,164,0.25);
}
.btn-danger:hover:not(:disabled) {
  filter: brightness(0.9); transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220,38,38,0.22);
}
.btn-primary:active:not(:disabled),
.btn-danger:active:not(:disabled) { transform: translateY(0); filter: brightness(0.86); }
.btn-primary:disabled,
.btn-danger:disabled { cursor: not-allowed; opacity: 0.38; box-shadow: none; transform: none; }

/* =============================================================  TABLES  ============================================================= */
.table-container {
  border-radius: var(--radius-md);
  overflow: hidden; border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
}

/* =============================================================  UTILITY  ============================================================= */
.subtitle {
  color: var(--text-muted); font-size: 0.875rem;
  margin: 0.3rem 0 1.5rem; line-height: 1.6; font-weight: 400;
}
.results { margin-top: 1.5rem; }

.skills-grid {
  display: grid; gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}
.skills-card {
  padding: 1.1rem; border-radius: var(--radius-md);
  background: var(--surface); border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
}
.skills-card h4 { margin: 0 0 0.65rem; font-weight: 700; color: var(--text-soft); }

/* =============================================================  AUTH NAV  ============================================================= */
.nav-btn-login { color: var(--text-muted) !important; font-weight: 500 !important; }

.nav-btn-register {
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--primary); color: #FFFFFF !important;
  font-weight: 600; font-size: 0.875rem;
  padding: 0.45rem 0.9rem; border-radius: var(--radius-sm);
  text-decoration: none;
  transition: background 0.15s ease, transform 0.15s ease;
}
.nav-btn-register:hover { background: var(--primary-dark); transform: translateY(-1px); }

/* =============================================================  USER AVATAR  ============================================================= */
.user-profile-btn {
  display: flex; align-items: center; gap: 0.45rem;
  background: transparent; border: none; cursor: pointer;
  padding: 0.35rem 0.6rem; border-radius: var(--radius-sm);
  transition: background 0.15s;
}
.user-profile-btn:hover { background: var(--surface-2); }

.nav-avatar {
  width: 1.75rem; height: 1.75rem; border-radius: 50%;
  background: var(--primary); color: #FFFFFF;
  display: flex; justify-content: center; align-items: center;
  font-size: 0.75rem; font-weight: 700; flex-shrink: 0;
}

.nav-username {
  max-width: 110px; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap;
  font-size: 0.875rem; font-weight: 500; color: var(--text-soft);
}

.user-dropdown-content { right: 0; left: auto; min-width: 188px; }

.user-info-header {
  padding: 0.55rem 0.8rem;
  border-bottom: 1px solid var(--border); margin-bottom: 3px;
}
.header-name { margin: 0; font-weight: 600; font-size: 0.875rem; color: var(--text); }
.header-role { margin: 0; font-size: 0.72rem; color: var(--text-muted); margin-top: 1px; }

.dropdown-logout-btn {
  width: 100%; display: flex; align-items: center; gap: 0.45rem;
  background: transparent; border: none;
  padding: 0.5rem 0.8rem; color: var(--danger);
  font-weight: 500; font-size: 0.875rem;
  text-align: left; cursor: pointer; border-radius: var(--radius-xs);
  transition: background 0.12s ease;
}
.dropdown-logout-btn:hover { background: var(--danger-bg); }

/* =============================================================  MOBILE  ============================================================= */
@media (max-width: 768px) {
  .nav-inner { height: auto; padding: 0.65rem 1rem; flex-wrap: wrap; }
  .menu-toggle { display: inline-flex; }
  .nav-links {
    display: none; width: 100%; flex-direction: column;
    align-items: stretch; gap: 0.25rem; padding: 0.5rem 0 0.35rem;
  }
  .nav-links.is-open { display: flex; }
  .nav-link,
  .dropdown-btn {
    width: 100%; justify-content: flex-start;
    padding: 0.65rem 0.85rem;
    background: var(--surface-2); border-radius: var(--radius-sm);
  }
  .nav-spacer { display: none; }
  .dropdown { width: 100%; }
  .dropdown-content {
    position: static; width: 100%; min-width: 0;
    margin-top: 2px; padding: 3px;
    box-shadow: none; border-radius: var(--radius-sm);
    background: var(--surface-2); border-color: transparent;
  }
  .dropdown:hover .dropdown-content { display: none; }
  .dropdown.is-open .dropdown-content { display: block; }
  .dropdown-content a { white-space: normal; }
  .main-content { padding: 1.25rem 1rem 2rem; }
  .view-container { padding: 1.25rem 1rem; }
  .btn-primary,
  .btn-danger { width: 100%; justify-content: center; }
}

@media (max-width: 420px) {
  .brand-text { max-width: 150px; overflow: hidden; text-overflow: ellipsis; }
}
</style>

