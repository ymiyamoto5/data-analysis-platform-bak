<template>
  <div id="app">
    <ModalDialog v-if="$store.state.showModalDialog" />
    <MainWindow />
  </div>
</template>

<script>
import MainWindow from '@/views/MainWindow.vue'

export default {
  name: 'app',
  components: {
    MainWindow,
  },
}
</script>
