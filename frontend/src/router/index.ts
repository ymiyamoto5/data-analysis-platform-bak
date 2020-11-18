import Vue from 'vue'
import VueRouter, { RouteConfig } from 'vue-router'
import Manager from '../views/Manager.vue'

Vue.use(VueRouter)

const routes: Array<RouteConfig> = [
  {
    path: '/',
    name: 'Manager',
    component: Manager
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
