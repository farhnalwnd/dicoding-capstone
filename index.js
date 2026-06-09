import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ScrapeView from '../views/ScrapeView.vue'
import AnalyzeView from '../views/AnalyzeView.vue'
import HRRankView from '../views/HRRankView.vue'
import SemanticSearchView from '../views/SemanticSearchView.vue'
import ClusterView from '../views/ClusterView.vue'

const routes = [
  { path: '/', component: HomeView, meta: { title: 'Home' } },
  { path: '/jobseeker/scrape', component: ScrapeView, meta: { title: 'Scrape Jobs' } },
  { path: '/jobseeker/analyze', component: AnalyzeView, meta: { title: 'CV-JD Analysis' } },
  { path: '/jobseeker/search', component: SemanticSearchView, meta: { title: 'Semantic Job Search' } },
  { path: '/hr/rank', component: HRRankView, meta: { title: 'Bulk CV Ranking' } },
  { path: '/hr/cluster', component: ClusterView, meta: { title: 'Talent Clustering' } }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
