import ConfirmDialog from '@/components/ConfirmDialog'
import DatetimePicker from '@/components/DatetimePicker'
import ErrorSnackbar from '@/components/ErrorSnackbar'
import router from '@/router'
import store from '@/store/store'
import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
Vue.component('ConfirmDialog', ConfirmDialog)
Vue.component('v-datetime-picker', DatetimePicker)
Vue.component('ErrorSnackbar', ErrorSnackbar)

Vue.config.productionTip = false

new Vue({
  router,
  vuetify,
  store,
  render: (h) => h(App),
}).$mount('#app')
