import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import router from '@/router'
import store from '@/store/store'
import ConfirmDialog from '@/components/ConfirmDialog'
import ErrorDialog from '@/components/ErrorDialog'
Vue.component('ConfirmDialog', ConfirmDialog)
Vue.component('ErrorDialog', ErrorDialog)

Vue.config.productionTip = false

new Vue({
  router,
  vuetify,
  store,
  render: (h) => h(App),
}).$mount('#app')
