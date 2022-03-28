<template>
  <div>
    <v-snackbar
      v-model="$store.state.showErrorSnackbar"
      timeout="10000"
      top
      color="error"
    >
      <h3>{{ $store.state.errorHeader }}</h3>
      <div class="errorMsg">{{ $store.state.errorMsg }}</div>
      <template v-slot:action="{ attrs }">
        <v-btn
          color="white"
          text
          v-bind="attrs"
          @click="$store.commit('setShowErrorSnackbar', false)"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script></script>

<style scoped>
.errorMsg {
  white-space: pre-line;
  word-wrap: break-word;
}
</style>
