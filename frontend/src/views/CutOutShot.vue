<template>
  <v-app>
    <v-container>
      <v-row dense>
        <v-col cols="5">
          <MachineSelect @input="setMachine"></MachineSelect>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="7">
          <CollectDataSelect
            @input="setCollectData"
            :value="machine_id"
          ></CollectDataSelect>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="1">
          <DisplacementRangeSlider
            v-if="dataSelected"
            @input="setDisplacementRange"
            :targetDir="targetDir"
          ></DisplacementRangeSlider>
        </v-col>
        <v-col cols="11">
          <ChartCard :machine_id="machine_id" :targetDir="targetDir" />
        </v-col>
      </v-row>
      <v-row justify="center" v-if="dataSelected">
        <v-btn color="primary" @click="start" :disabled="running"
          >ショット切り出し開始</v-btn
        >
      </v-row>
      <v-row justify="center">
        <v-progress-circular
          v-if="started === true && running === true"
          indeterminate
          color="#53e09c"
        />
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import MachineSelect from '@/components/CutOutShot/MachineSelect.vue'
import CollectDataSelect from '@/components/CutOutShot/CollectDataSelect.vue'
import ChartCard from '@/components/CutOutShot/ChartCard.vue'
import DisplacementRangeSlider from '@/components/CutOutShot/DisplacementRangeSlider.vue'

const TARGET_DIR_API_URL = '/api/v1/target_dir'
const CUT_OUT_SHOT_API_URL = '/api/v1/cut_out_shot'

export default {
  components: {
    MachineSelect,
    DisplacementRangeSlider,
    CollectDataSelect,
    ChartCard,
  },
  data() {
    return {
      dataSelected: false,
      started: false,
      running: false,
      machine_id: '',
      targetDir: '',
      start_displacement: 0,
      end_displacement: 0,
      collectData: '',
    }
  },
  methods: {
    setMachine(value) {
      this.machine_id = value
    },
    setCollectData(value) {
      this.collectData = value
      this.dataSelected = true
      this.fetchTargetDir()
    },
    // 対象ディレクトリ名を取得
    fetchTargetDir: async function() {
      // ex) 2021/09/06 14:59:38 - 2021/09/06 15:00:00 => 2021/09/06 14:59:38 => UNIXTIME(ミリ秒)
      const targetDate = Date.parse(this.collectData.split('-')[0].slice(0, -1))

      const client = createBaseApiClient()
      await client
        .get(TARGET_DIR_API_URL, {
          params: {
            machine_id: this.machine_id,
            targetDate: targetDate,
          },
        })
        .then((res) => {
          if (res.data === null) {
            return
          }
          this.targetDir = res.data
        })
        .catch((e) => {
          console.log(e.response.data.message)
        })
    },
    setDisplacementRange(range) {
      this.start_displacement = range[1]
      this.end_displacement = range[0]
    },
    // ショット切り出し開始
    start: async function() {
      this.started = true
      this.running = true

      const postData = {
        machine_id: this.machine_id,
        start_displacement: this.start_displacement,
        end_displacement: this.end_displacement,
        target_dir: this.targetDir,
      }

      const client = createBaseApiClient()
      await client
        .post(CUT_OUT_SHOT_API_URL, postData)
        .then(() => {
          this.running = false
        })
        .catch((e) => {
          console.log(e.response.data.message)
        })
    },
  },
}
</script>

<style scoped></style>
