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
    // ErrorSnackbar
    showErrorSnackbar: false,
    errorHeader: '',
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
    // ErrorSnackbar
    setShowErrorSnackbar(state, showErrorSnackbar) {
      state.showErrorSnackbar = showErrorSnackbar
    },
    setErrorHeader(state, errorHeader) {
      state.errorHeader = errorHeader
    },
    setErrorMsg(state, errorMsg) {
      state.errorMsg = errorMsg
    },
  },
})
