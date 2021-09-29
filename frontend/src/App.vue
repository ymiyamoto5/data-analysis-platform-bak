<template>
  <div id="app">
    <ConfirmDialog v-if="$store.state.showConfirmDialog" />
    <ErrorDialog v-if="$store.state.showErrorDialog" />
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
