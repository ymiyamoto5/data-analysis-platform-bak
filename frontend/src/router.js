import Vue from 'vue'
import VueRouter from 'vue-router'

export const ROOT_NAME = 'root'
export const ROOT_PATH = '/'
export const DATA_COLLECT_NAME = 'data_collect'
export const DATA_COLLECT_PATH = ROOT_PATH + DATA_COLLECT_NAME
export const DATA_COLLECT_HISTORY_NAME = 'data_collect_history'
export const DATA_COLLECT_HISTORY_PATH = ROOT_PATH + DATA_COLLECT_HISTORY_NAME
export const SETTINGS_NAME = 'settings'
export const SETTINGS_PATH = ROOT_PATH + SETTINGS_NAME
export const MACHINE_SETTINGS_NAME = 'machine'
export const MACHINE_SETTINGS_PATH = SETTINGS_PATH + '/' + MACHINE_SETTINGS_NAME
export const GATEWAY_SETTINGS_NAME = 'gateway'
export const GATEWAY_SETTINGS_PATH = SETTINGS_PATH + '/' + GATEWAY_SETTINGS_NAME
export const HANDLER_SETTINGS_NAME = 'handler'
export const HANDLER_SETTINGS_PATH = SETTINGS_PATH + '/' + HANDLER_SETTINGS_NAME
export const SENSOR_SETTINGS_NAME = 'sensor'
export const SENSOR_SETTINGS_PATH = SETTINGS_PATH + '/' + SENSOR_SETTINGS_NAME

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
    path: SETTINGS_PATH,
    component: () => import('@/views/Settings.vue'),
    children: [
      // default path
      {
        path: '',
        redirect: MACHINE_SETTINGS_PATH,
      },
      {
        path: MACHINE_SETTINGS_PATH,
        name: MACHINE_SETTINGS_NAME,
        component: () => import('@/views/MachineSettings.vue'),
      },
      {
        path: GATEWAY_SETTINGS_PATH,
        name: GATEWAY_SETTINGS_NAME,
        component: () => import('@/views/GatewaySettings.vue'),
      },
      {
        path: HANDLER_SETTINGS_PATH,
        name: HANDLER_SETTINGS_NAME,
        component: () => import('@/views/HandlerSettings.vue'),
      },
      {
        path: SENSOR_SETTINGS_PATH,
        name: SENSOR_SETTINGS_NAME,
        component: () => import('@/views/SensorSettings.vue'),
      },
    ],
  },
]

Vue.use(VueRouter)
export default new VueRouter({
  routes,
})
