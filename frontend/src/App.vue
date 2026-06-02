<template>
  <div id="app">
    <!-- Full-width vibrant background decoration -->
    <div class="bg-gradient-mesh">
      <div class="mesh-sphere sphere-1"></div>
      <div class="mesh-sphere sphere-2"></div>
      <div class="mesh-sphere sphere-3"></div>
    </div>

    <!-- 100% Screen Width Glassmorphism Navbar -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <router-link to="/">
            <span class="brand-text">CV Matcher</span>
            <span class="brand-accent">Pro</span>
          </router-link>
        </div>
        
        <div class="nav-links">
          <router-link to="/" class="nav-link">Home</router-link>
          
          <!-- Job Seeker Dropdown -->
          <div class="dropdown">
            <button class="dropdown-btn">
              Job Seeker <span class="arrow">▼</span>
            </button>
            <div class="dropdown-content glass-panel">
              <router-link to="/jobseeker/scrape">Scrape Jobs</router-link>
              <router-link to="/jobseeker/analyze">CV-JD Analysis</router-link>
              <router-link to="/jobseeker/search">Semantic Search</router-link>
            </div>
          </div>

          <!-- HR Dropdown -->
          <div class="dropdown">
            <button class="dropdown-btn">
              HR Panel <span class="arrow">▼</span>
            </button>
            <div class="dropdown-content glass-panel">
              <router-link to="/hr/rank">Bulk CV Ranking</router-link>
              <router-link to="/hr/cluster">Talent Clustering</router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content Area -->
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<style>
/* Design System Variables & Imports */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

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
}

/* 100% Screen Width Glassmorphism Navbar */
.navbar {
  width: 100%;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border-bottom: 1px solid var(--glass-border);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
}

.nav-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
}

.nav-brand a {
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.brand-text {
  color: var(--primary);
}

.brand-accent {
  color: var(--cta);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: var(--text);
  text-decoration: none;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.nav-link:hover, .router-link-active {
  background: rgba(3, 105, 161, 0.08);
  color: var(--primary);
}

/* Dropdown styling */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-btn {
  background: none;
  border: none;
  color: var(--text);
  font-weight: 600;
  font-size: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: inherit;
  transition: all 0.2s ease;
}

.dropdown-btn:hover {
  background: rgba(3, 105, 161, 0.08);
  color: var(--primary);
}

.arrow {
  font-size: 0.7rem;
  transition: transform 0.2s ease;
}

.dropdown:hover .arrow {
  transform: rotate(180deg);
}

.dropdown-content {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 220px;
  margin-top: 0.5rem;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 0.5rem 0;
  z-index: 1100;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown-content a {
  display: block;
  padding: 0.75rem 1.25rem;
  color: var(--text);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.dropdown-content a:hover {
  background: rgba(3, 105, 161, 0.1);
  color: var(--primary);
  padding-left: 1.5rem;
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
.router-view-anim-enter-active, .router-view-anim-leave-active {
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
  .nav-container {
    padding: 1rem;
  }
  
  .nav-links {
    gap: 0.5rem;
  }
  
  .nav-link, .dropdown-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
  }
  
  .main-content {
    padding: 1.5rem 1rem;
  }
}
</style>
