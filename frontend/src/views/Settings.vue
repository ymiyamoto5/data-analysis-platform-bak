<template>
  <div>
    <template v-for="item in items">
      <router-link :key="item.name" :to="item.link">
        {{ item.name }}
      </router-link>
      <!-- <v-divider :key="item.name" class="mx-4" inset vertical></v-divider> -->
    </template>
    <router-view />
  </div>
</template>

<script>
import {
  MACHINE_SETTINGS_PATH,
  GATEWAY_SETTINGS_PATH,
  HANDLER_SETTINGS_PATH,
  SENSOR_SETTINGS_PATH,
} from '@/router'

export default {
  name: 'settings',
  components: {},
  data() {
    return {
      items: [
        {
          id: 'machine',
          name: '機器',
          link: MACHINE_SETTINGS_PATH,
        },
        {
          id: 'gateway',
          name: 'ゲートウェイ',
          link: GATEWAY_SETTINGS_PATH,
        },
        {
          id: 'handler',
          name: 'ハンドラー',
          link: HANDLER_SETTINGS_PATH,
        },
        {
          id: 'sensor',
          name: 'センサー',
          link: SENSOR_SETTINGS_PATH,
        },
      ],
    }
  },
}
</script>

<style scoped>
/* #v-main {
  margin: 10px;
  padding: 10px;
} */
</style>
