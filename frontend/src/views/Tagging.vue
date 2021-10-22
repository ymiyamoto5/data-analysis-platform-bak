<template>
  <v-app>
    <v-container>
      <v-row dense>
        <v-col cols="5">
          <MachineSelect @input="setMachine"></MachineSelect>
        </v-col>
      </v-row>
      <!-- <v-row dense>
        <v-col cols="7">
          <CollectDataSelect
            @input="setCollectData"
            :value="machineId"
          ></CollectDataSelect>
        </v-col>
      </v-row> -->

      <v-row justify="center" v-if="dataSelected">
        <v-btn
          color="primary"
          @click="start"
          :disabled="running"
          :loading="running"
          >ショット切り出し開始</v-btn
        >
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
// import { createBaseApiClient } from '@/api/apiBase'
import MachineSelect from '@/components/MachineSelect.vue'

export default {
  components: {
    MachineSelect,
  },
  data() {
    return {
      dataSelected: false,
      machineId: '',
      targetDateStr: '', // yyyyMMdd文字列
    }
  },
  methods: {
    setMachine(value) {
      this.targetDateStr = ''
      this.machineId = value
    },
  },
}
</script>

<style scoped></style>
