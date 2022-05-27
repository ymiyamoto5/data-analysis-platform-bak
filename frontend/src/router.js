import Vue from 'vue'
import VueRouter from 'vue-router'

export const ROOT_NAME = 'root'
export const ROOT_PATH = '/'
export const DATA_COLLECT_NAME = 'data_collect'
export const DATA_COLLECT_PATH = ROOT_PATH + DATA_COLLECT_NAME
export const DATA_COLLECT_HISTORY_NAME = 'data_collect_history'
export const DATA_COLLECT_HISTORY_PATH = ROOT_PATH + DATA_COLLECT_HISTORY_NAME
export const CUT_OUT_SHOT_NAME = 'cut_out_shot'
export const CUT_OUT_SHOT_PATH = ROOT_PATH + CUT_OUT_SHOT_NAME
export const TAGGING_NAME = 'tagging'
export const TAGGING_PATH = ROOT_PATH + TAGGING_NAME
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
export const KIBANA_PATH = process.env.VUE_APP_KIBANA_URL
export const JUPYTER_PATH = process.env.VUE_APP_JUPYTER_URL
export const GOLLUM_PATH = process.env.VUE_APP_GOLLUM_URL
export const MODEL_MANAGEMENT_NAME = 'model_management'
export const MODEL_MANAGEMENT_PATH = ROOT_PATH + MODEL_MANAGEMENT_NAME
export const CSV_UPLOAD_NAME = 'csv_upload'
export const CSV_UPLOAD_PATH = ROOT_PATH + CSV_UPLOAD_NAME

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
    path: CUT_OUT_SHOT_PATH,
    name: CUT_OUT_SHOT_NAME,
    component: () => import('@/views/CutOutShot.vue'),
  },
  {
    path: TAGGING_PATH,
    name: TAGGING_NAME,
    component: () => import('@/views/Tagging.vue'),
  },
  {
    path: MODEL_MANAGEMENT_PATH,
    name: MODEL_MANAGEMENT_NAME,
    component: () => import('@/views/ModelManagement.vue'),
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
  {
    path: '/kibana',
    // NOTE: 外部サイトを別タブで開く。noreferrerが無いと元タブがハングするので注意。
    beforeEnter() {
      window.open(KIBANA_PATH, '_blank', 'noreferrer')
    },
  },
  {
    path: '/jupyter',
    beforeEnter() {
      window.open(JUPYTER_PATH, '_blank', 'noreferrer')
    },
  },
  {
    path: '/gollum',
    beforeEnter() {
      window.open(GOLLUM_PATH, '_blank', 'noreferrer')
    },
  },
  {
    path: CSV_UPLOAD_PATH,
    name: CSV_UPLOAD_NAME,
    component: () => import('@/views/CsvUpload.vue'),
  },
]

Vue.use(VueRouter)
export default new VueRouter({
  routes,
})
