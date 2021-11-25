<template>
  <div id="app">
    <ConfirmDialog v-if="$store.state.showConfirmDialog" />
    <ErrorSnackbar v-if="$store.state.showErrorSnackbar" />
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
