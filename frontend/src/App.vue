<template>
  <div class="app-container">
    <Toast ref="toast" />

    <nav class="navbar">
      <div class="nav-inner">
        <router-link to="/" class="nav-brand" @click="closeMenus">
          <span class="brand-icon">CV</span>
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
          <router-link to="/" class="nav-link" @click="closeMenus">Home</router-link>

          <div class="dropdown" :class="{ 'is-open': openDropdown === 'jobseeker' }">
            <button class="dropdown-btn" type="button" @click="toggleDropdown('jobseeker')">
              <span>Job Seeker</span>
              <span class="arrow">▾</span>
            </button>
            <div class="dropdown-content">
              <router-link to="/jobseeker/scrape" @click="closeMenus">Scrape Jobs</router-link>
              <router-link to="/jobseeker/analyze" @click="closeMenus">CV-JD Analysis</router-link>
              <router-link to="/jobseeker/search" @click="closeMenus">Semantic Search</router-link>
            </div>
          </div>

          <div class="dropdown" :class="{ 'is-open': openDropdown === 'hr' }">
            <button class="dropdown-btn" type="button" @click="toggleDropdown('hr')">
              <span>HR Panel</span>
              <span class="arrow">▾</span>
            </button>
            <div class="dropdown-content">
              <router-link to="/hr/rank" @click="closeMenus">Bulk CV Ranking</router-link>
              <router-link to="/hr/cluster" @click="closeMenus">Talent Clustering</router-link>
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
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Toast from './components/Toast.vue'

const toast = ref(null)
const route = useRoute()
const isMobileMenuOpen = ref(false)
const openDropdown = ref(null)

function toggleDropdown(name) {
  openDropdown.value = openDropdown.value === name ? null : name
}

function closeMenus() {
  isMobileMenuOpen.value = false
  openDropdown.value = null
}

watch(() => route.fullPath, closeMenus)
</script>

<style>
/* Design System Variables & Imports */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

:root {
  --primary: #0369A1;
  --secondary: #0EA5E9;
  --cta: #22C55E;
  --text: #0C4A6E;
  --text-muted: #475569;
  --blur-amount: 18px;
  --glass-bg: rgba(255, 255, 255, 0.45);
  --glass-border: rgba(255, 255, 255, 0.4);
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--text);
  min-height: 100vh;
  background: #F0F9FF;
  position: relative;
  overflow-x: hidden;
}

.app-container {
  min-height: 100vh;
}

/* Background Vibrant Mesh */
.bg-gradient-mesh {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -10;
  overflow: hidden;
  pointer-events: none;
}

.mesh-sphere {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.45;
  animation: float 25s infinite ease-in-out;
}

.sphere-1 {
  top: -10%;
  left: -10%;
  width: 50vw;
  height: 50vw;
  background: radial-gradient(circle, #38BDF8 0%, #0369A1 100%);
}

.sphere-2 {
  bottom: -15%;
  right: -5%;
  width: 60vw;
  height: 60vw;
  background: radial-gradient(circle, #34D399 0%, #059669 100%);
  animation-delay: -5s;
}

.sphere-3 {
  top: 40%;
  left: 30%;
  width: 35vw;
  height: 35vw;
  background: radial-gradient(circle, #818CF8 0%, #4F46E5 100%);
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(50px) scale(1.15); }
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 100%;
  margin: 0;
  border-inline: none;
}

/* Responsive Navbar */
.navbar {
  width: 100%;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border-bottom: 1px solid var(--glass-border);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 4px 30px rgba(3, 105, 161, 0.06);
  text-align: left;
}

.nav-inner {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.9rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  box-sizing: border-box;
}

.nav-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: #fff;
  font-weight: 800;
  letter-spacing: -0.5px;
  box-shadow: 0 8px 18px rgba(3, 105, 161, 0.18);
}

.brand-text {
  color: var(--primary);
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.4px;
  white-space: nowrap;
}

.nav-links {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.65rem;
}

.nav-link,
.dropdown-btn {
  color: var(--text);
  text-decoration: none;
  font-weight: 700;
  font-size: 0.95rem;
  padding: 0.65rem 1rem;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.nav-link:hover,
.nav-link.router-link-active,
.dropdown-btn:hover,
.dropdown.is-open .dropdown-btn {
  background: rgba(3, 105, 161, 0.08);
  color: var(--primary);
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
  font-family: inherit;
}

.arrow {
  font-size: 0.75rem;
  transition: transform 0.2s ease;
}

.dropdown:hover .arrow,
.dropdown.is-open .arrow {
  transform: rotate(180deg);
}

.dropdown-content {
  display: none;
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  min-width: 230px;
  padding: 0.45rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border: 1px solid rgba(3, 105, 161, 0.12);
  box-shadow: 0 18px 40px rgba(3, 105, 161, 0.12);
  z-index: 1100;
}

.dropdown:hover .dropdown-content,
.dropdown.is-open .dropdown-content {
  display: block;
}

.dropdown-content a {
  display: block;
  padding: 0.75rem 0.95rem;
  color: var(--text);
  text-decoration: none;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.dropdown-content a:hover,
.dropdown-content a.router-link-active {
  background: rgba(3, 105, 161, 0.1);
  color: var(--primary);
}

.menu-toggle {
  display: none;
  width: 2.6rem;
  height: 2.6rem;
  border: 1px solid rgba(3, 105, 161, 0.14);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.55);
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
  background: var(--primary);
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

/* Main Content Area */
.main-content {
  flex: 1;
  padding: 2.5rem 2rem;
  max-width: 100%;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* Reusable Glass Panel Class */
.glass-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  box-shadow: 0 8px 32px 0 rgba(3, 105, 161, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-panel:hover {
  box-shadow: 0 12px 40px 0 rgba(3, 105, 161, 0.12);
}

.view-container {
  margin: 0 auto;
  padding: 3rem;
}

h2 {
  color: var(--primary);
  font-weight: 800;
  font-size: 2rem;
  margin-top: 0;
  margin-bottom: 0.5rem;
  letter-spacing: -0.5px;
}

.subtitle {
  color: var(--text-muted);
  font-size: 1.05rem;
  margin-bottom: 2.5rem;
}

/* Form Design */
.form-group {
  margin-bottom: 1.75rem;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.6rem;
  font-size: 0.95rem;
}

.input-field {
  width: 100%;
  padding: 0.85rem 1.2rem;
  border: 1px solid rgba(3, 105, 161, 0.25);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.85);
  font-family: inherit;
  font-size: 1rem;
  color: var(--text);
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.input-field:focus {
  outline: none;
  border-color: var(--secondary);
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.15);
  background: #FFFFFF;
}

.file-input {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
}

/* Custom Table customisations */
.table-container {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
}

/* Animations */
.router-view-anim-enter-active,
.router-view-anim-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.router-view-anim-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.router-view-anim-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 768px) {
  .nav-inner {
    padding: 0.8rem 1rem;
    flex-wrap: wrap;
  }

  .brand-icon {
    width: 2rem;
    height: 2rem;
    border-radius: 10px;
    font-size: 0.9rem;
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
    box-sizing: border-box;
    padding: 0.85rem 1rem;
    background: rgba(255, 255, 255, 0.4);
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
    box-sizing: border-box;
    box-shadow: none;
    background: rgba(255, 255, 255, 0.55);
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
    padding: 1.5rem 1rem;
  }

  .view-container {
    padding: 1.5rem;
  }
}

@media (max-width: 420px) {
  .brand-text {
    max-width: 170px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
