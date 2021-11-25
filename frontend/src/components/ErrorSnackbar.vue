<template>
  <div>
    <v-snackbar
      v-model="$store.state.showErrorSnackbar"
      timeout="10000"
      top
      color="error"
    >
      <h3>{{ $store.state.errorHeader }}</h3>
      {{ $store.state.errorMsg }}
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
