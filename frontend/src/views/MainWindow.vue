<template>
  <v-app>
    <v-navigation-drawer app permanent expand-on-hover class="primary" dark>
      <v-list nav>
        <template v-for="item in items">
          <v-list-item :key="item.name" :to="item.link">
            <v-list-item-icon>
              <v-icon large dark>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ item.name }}</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import {
  DATA_COLLECT_PATH,
  DATA_COLLECT_HISTORY_PATH,
  SETTINGS_PATH,
} from '@/router'

export default {
  name: 'main-window',
  components: {},
  data() {
    return {
      items: [
        {
          id: 'dataCollect',
          name: 'データ収集',
          icon: 'mdi-home',
          link: DATA_COLLECT_PATH,
        },
        {
          id: 'dataCollectHistory',
          name: 'データ収集履歴',
          icon: 'mdi-history',
          link: DATA_COLLECT_HISTORY_PATH,
        },
        {
          id: 'settings',
          name: '設定',
          icon: 'mdi-cog-outline',
          link: SETTINGS_PATH,
        },
      ],
    }
  },
}
</script>

<style scoped>
#v-main {
  margin: 10px;
  padding: 10px;
}
</style>
