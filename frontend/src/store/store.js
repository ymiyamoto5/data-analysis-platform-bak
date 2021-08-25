import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  strict: true,
  namespaced: true,
  state: {
    // ConfirmDialog
    showConfirmDialog: false,
    confirmMsg: '',
    callbackFunc: null,
    callbackFuncParam: null,
    // ErrorDialog
    showErrorDialog: false,
    errorMsg: '',
  },
  mutations: {
    // ConfirmDialog
    setShowConfirmDialog(state, showConfirmDialog) {
      state.showConfirmDialog = showConfirmDialog
    },
    setConfirmMsg(state, confirmMsg) {
      state.confirmMsg = confirmMsg
    },
    setCallbackFunc(state, callbackFunc) {
      state.callbackFunc = callbackFunc
    },
    setCallbackFuncParam(state, callbackFuncParam) {
      state.callbackFuncParam = callbackFuncParam
    },
    // ErrorDialog
    setShowErrorDialog(state, showErrorDialog) {
      state.showErrorDialog = showErrorDialog
    },
    setErrorMsg(state, errorMsg) {
      state.errorMsg = errorMsg
    },
  },
})
