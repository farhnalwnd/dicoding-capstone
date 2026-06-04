import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import Vue3EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'
import ModelInfoBadge from './components/ModelInfoBadge.vue'

const app = createApp(App)
app.component('EasyDataTable', Vue3EasyDataTable)
app.component('ModelInfoBadge', ModelInfoBadge)
app.use(router)
app.mount('#app')
