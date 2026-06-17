import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ScrapeView from '../views/ScrapeView.vue'
import AnalyzeView from '../views/AnalyzeView.vue'
import HRRankView from '../views/HRRankView.vue'
import SemanticSearchView from '../views/SemanticSearchView.vue'
import TalentPoolView from '../views/TalentPoolView.vue'
import InterviewSchedulerView from '../views/InterviewSchedulerView.vue'
import HRDashboardView from '../views/HRDashboardView.vue'
import ResumeAdvisorView from '../views/ResumeAdvisorView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import UserManagementView from '../views/UserManagementView.vue'
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
  {
    path: '/resume-advisor',
    component: ResumeAdvisorView,
    meta: {
      title: 'AI Resume Advisor',
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
    path: '/hr/talent-pool', 
    component: TalentPoolView, 
    meta: { 
      title: 'Talent Pool',
      requiresAuth: true,
      roles: ['hr']
    } 
  },
  { 
    path: '/hr/interviews', 
    component: InterviewSchedulerView, 
    meta: { 
      title: 'Interview Scheduler',
      requiresAuth: true,
      roles: ['hr']
    } 
  },
  { 
    path: '/hr-dashboard', 
    component: HRDashboardView, 
    meta: { 
      title: 'HR Analytics',
      requiresAuth: true,
      roles: ['hr']
    } 
  },

  // Admin Routes (Protected)
  {
    path: '/admin',
    component: AdminDashboardView,
    meta: {
      title: 'Admin Control Center',
      requiresAuth: true,
      roles: ['admin']
    }
  },
  {
    path: '/admin/users',
    component: UserManagementView,
    meta: {
      title: 'User Management',
      requiresAuth: true,
      roles: ['admin']
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

  // Helper: get default landing page per role
  function getHomePage(role) {
    if (role === 'admin') return '/admin'
    if (role === 'hr')    return '/hr-dashboard'
    return '/dashboard'
  }

  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      // Not logged in → go to login
      next('/login')
    } else if (to.meta.roles && !to.meta.roles.includes(userRole)) {
      // Logged in but wrong role → redirect to their own home page
      next(getHomePage(userRole))
    } else {
      next()
    }
  } else {
    // Public route: if already logged in and tries /login or /register → redirect home
    if (isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      next(getHomePage(userRole))
    } else {
      next()
    }
  }
})

export default router
