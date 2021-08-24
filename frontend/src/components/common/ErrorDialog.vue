<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-card-title class="text-h6 grey lighten-2">
          エラー
        </v-card-title>

        <v-card-text>
          {{ errorMessage }}
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="dialog = false">
            I accept
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'error-dialog',
  props: ['dialog', 'errorMessage'],
  data() {
    return {
      dialog: this.dialog,
      errorMessage: this.errorMessage,
    }
  },
}
</script>
