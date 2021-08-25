import Vue from 'vue'
import VueRouter from 'vue-router'

export const ROOT_NAME = 'root'
export const ROOT_PATH = '/'
export const DATA_COLLECT_NAME = 'data_collect'
export const DATA_COLLECT_PATH = ROOT_PATH + DATA_COLLECT_NAME
export const DATA_COLLECT_HISTORY_NAME = 'data_collect_history'
export const DATA_COLLECT_HISTORY_PATH = ROOT_PATH + DATA_COLLECT_HISTORY_NAME
export const CONFIGURE_NAME = 'configure'
export const CONFIGURE_PATH = ROOT_PATH + CONFIGURE_NAME

const routes = [
  // '/'へのアクセスは/data_collectにリダイレクト
  {
    path: ROOT_PATH,
    redirect: DATA_COLLECT_PATH,
  },
  {
    path: DATA_COLLECT_PATH,
    name: DATA_COLLECT_NAME,
    component: () => import('@/views/DataCollect.vue'),
  },
  {
    path: DATA_COLLECT_HISTORY_PATH,
    name: DATA_COLLECT_HISTORY_NAME,
    component: () => import('@/views/DataCollectHistory.vue'),
  },
  {
    path: CONFIGURE_PATH,
    name: CONFIGURE_NAME,
    component: () => import('@/views/Configure.vue'),
  },
]

Vue.use(VueRouter)
export default new VueRouter({
  routes,
})
