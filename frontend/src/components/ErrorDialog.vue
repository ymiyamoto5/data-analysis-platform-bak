<template>
  <transition name="modal">
    <div class="modal-mask">
      <div class="modal-wrapper">
        <div class="modal-container">
          <div class="modal-header"></div>

          <div class="modal-body">
            {{ $store.state.errorMsg }}
          </div>

          <button
            class="btn"
            @click="$store.commit('setShowErrorDialog', false)"
          >
            閉じる
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'ConfirmDialog',
  methods: {
    do_yes() {
      this.$store.state.callbackFunc(this.$store.state.callbackFuncParam)
      this.$store.commit('setShowConfirmDialog', false)
    },
  },
}
</script>

<style scoped>
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: table;
  transition: opacity 0.3s ease;
}
/* 画面上下真ん中に配置 */
.modal-wrapper {
  display: table-cell;
  vertical-align: middle;
}
/* ポップアップ外枠 */
.modal-container {
  width: 300px;
  margin: 0px auto;
  background-color: #fff;
  border-radius: 5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
  transition: all 0.3s ease;
}
/* ヘッダー */
.modal-header {
  display: block;
  text-align: center;
  border: 0px;
  padding: 20px 0 0 0;
  font-weight: bold;
}
/* ボディ */
.modal-body {
  display: block;
  text-align: center;
  padding: 5px 15px 0 15px;
  border: 0px;
  font-size: 0.9rem;
}
/* ボタン達 */
/* .btns {
  display: inline-block;
  margin-top: 15px;
  width: 300px;
} */
/* ボタン */
.btn {
  display: block;
  margin-top: 15px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  border: 1px solid #ddd;
  color: rgb(66, 133, 245);
  height: 50px;
}
.btn + .btn {
  border-left: 1px solid #ddd;
}

/*
  * The following styles are auto-applied to elements with
  * transition="modal" when their visibility is toggled
  * by Vue.js.
  *
  * You can easily play with the modal transition by editing
  * these styles.
  */

.modal-enter {
  opacity: 0;
}
.modal-leave-active {
  opacity: 0;
}
.modal-enter .modal-container,
.modal-leave-active .modal-container {
  -webkit-transform: scale(1.1);
  transform: scale(1.1);
}
</style>
