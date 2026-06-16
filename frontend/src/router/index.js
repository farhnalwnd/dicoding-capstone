import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ScrapeView from '../views/ScrapeView.vue'
import AnalyzeView from '../views/AnalyzeView.vue'
import HRRankView from '../views/HRRankView.vue'
import SemanticSearchView from '../views/SemanticSearchView.vue'
import ClusterView from '../views/ClusterView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import { authState } from '../stores/auth'

const routes = [
  // Public Routes
  { path: '/', component: HomeView, meta: { title: 'Home' } },
  { path: '/login', component: LoginView, meta: { title: 'Login' } },
  { path: '/register', component: RegisterView, meta: { title: 'Register' } },

  // Protected Dashboard
  { 
    path: '/dashboard', 
    component: DashboardView, 
    meta: { 
      title: 'Dashboard',
      requiresAuth: true,
      roles: ['hr', 'jobseeker']
    } 
  },

  // Job Seeker Routes (Protected)
  { 
    path: '/jobseeker/scrape', 
    component: ScrapeView, 
    meta: { 
      title: 'Scrape Jobs',
      requiresAuth: true,
      roles: ['jobseeker']
    } 
  },
  { 
    path: '/jobseeker/analyze', 
    component: AnalyzeView, 
    meta: { 
      title: 'CV-JD Analysis',
      requiresAuth: true,
      roles: ['jobseeker']
    } 
  },
  { 
    path: '/jobseeker/search', 
    component: SemanticSearchView, 
    meta: { 
      title: 'Semantic Job Search',
      requiresAuth: true,
      roles: ['jobseeker']
    } 
  },

  // HR Routes (Protected)
  { 
    path: '/hr/rank', 
    component: HRRankView, 
    meta: { 
      title: 'Bulk CV Ranking',
      requiresAuth: true,
      roles: ['hr']
    } 
  },
  { 
    path: '/hr/cluster', 
    component: ClusterView, 
    meta: { 
      title: 'Talent Clustering',
      requiresAuth: true,
      roles: ['hr']
    } 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!authState.token
  const userRole = authState.user?.role

  // If route requires auth
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      // Not logged in, redirect to login
      next('/login')
    } else if (to.meta.roles && !to.meta.roles.includes(userRole)) {
      // Logged in but doesn't have required role, redirect to dashboard
      next('/dashboard')
    } else {
      // Logged in and authorized
      next()
    }
  } else {
    // Route is public. If logged in and trying to access login/register, redirect to dashboard
    if (isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router
