<template>
  <div id="common-dialog">
    <v-dialog width="20rem">
      <v-card>
        <v-card-title class="headline grey lighten-2">
          {{ title }}
        </v-card-title>
        <v-card-text>
          {{ message }}
        </v-card-text>
      </v-card>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <div class="right-align-wrapper">
          <v-btn type="primary" @click.stop="closeConfirm">閉じる</v-btn>
        </div>
      </v-card-actions>
    </v-dialog>
  </div>
</template>

<script></script>
