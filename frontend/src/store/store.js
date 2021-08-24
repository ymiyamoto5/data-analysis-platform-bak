import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  strict: true,
  namespaced: true,
  state: {
    showModalDialog: false,
    modal_msg: '',
    callback_func: null,
    callback_func_param: null,
  },
  mutations: {
    set_showModalDialog(state, showModalDialog) {
      state.showModalDialog = showModalDialog
    },
    set_modal_msg(state, modal_msg) {
      state.modal_msg = modal_msg
    },
    set_callback_func(state, callback_func) {
      state.callback_func = callback_func
    },
    set_callback_func_param(state, callback_func_param) {
      state.callback_func_param = callback_func_param
    },
  },
})
