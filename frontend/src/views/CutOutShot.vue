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
            :value="machineId"
          ></CollectDataSelect>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="1">
          <DisplacementRangeSlider
            v-if="dataSelected"
            @input="setDisplacementRange"
            :targetDateStr="targetDateStr"
          ></DisplacementRangeSlider>
        </v-col>
        <v-col cols="9">
          <ChartCard
            :machineId="machineId"
            :targetDateStr="targetDateStr"
            :startDisplacement="startDisplacement"
            :endDisplacement="endDisplacement"
            :page="page"
            @setMaxPage="setMaxPage"
          />
        </v-col>
      </v-row>
      <v-row justify="space-around">
        <v-col cols="1">
          <v-icon v-if="dataSelected && displayPrevPage" @click="decrementPage"
            >mdi-arrow-left-bold-box-outline</v-icon
          >
        </v-col>
        <v-col cols="1">
          <v-icon v-if="dataSelected && displayNextPage" @click="incrementPage"
            >mdi-arrow-right-bold-box-outline</v-icon
          >
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

const TARGET_DIR_API_URL = '/api/v1/cut_out_shot/target_dir/'
const CUT_OUT_SHOT_DISPLACEMENT_API_URL = '/api/v1/cut_out_shot/displacement/'
// const CUT_OUT_SHOT_PULSE_API_URL = '/api/v1/cut_out_shot/pulse/'

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
      page: 0, // グラフの表示ファイル
      maxPage: 0, // グラフの最大ページング数（対象データのファイル数）
      displayPrevPage: false, // グラフを前に戻せるか
      displayNextPage: false, // グラフを先に進められるか
      machineId: '',
      targetDateStr: '',
      startDisplacement: 0,
      endDisplacement: 0,
      collectData: '',
    }
  },
  methods: {
    setMachine(value) {
      this.machineId = value
    },
    setCollectData(value) {
      this.collectData = value
      this.dataSelected = true
      this.fetchTargetDir()
      this.page = 0
      this.maxPage = 0
      this.displayPrevPage = false
      this.displayNextPage = false
    },
    // 対象ディレクトリ名を取得
    fetchTargetDir: async function() {
      // ex) 2021/09/06 14:59:38 - 2021/09/06 15:00:00 => 2021/09/06 14:59:38 => UNIXTIME(ミリ秒)
      const targetDate = Date.parse(this.collectData.split('-')[0].slice(0, -1))

      const client = createBaseApiClient()
      await client
        .get(TARGET_DIR_API_URL, {
          params: {
            machine_id: this.machineId,
            target_date_timestamp: targetDate,
          },
        })
        .then((res) => {
          if (res.data === null) {
            return
          }
          this.targetDateStr = res.data
        })
        .catch((e) => {
          console.log(e.response.data.detail)
        })
    },
    setDisplacementRange(range) {
      this.startDisplacement = range[1]
      this.endDisplacement = range[0]
    },
    // ショット切り出し開始
    start: async function() {
      this.started = true
      this.running = true

      const postData = {
        machine_id: this.machineId,
        start_displacement: this.startDisplacement,
        end_displacement: this.endDisplacement,
        target_date_str: this.targetDateStr,
      }

      const client = createBaseApiClient()
      await client
        .post(CUT_OUT_SHOT_DISPLACEMENT_API_URL, postData)
        .then(() => {
          this.running = false
        })
        .catch((e) => {
          console.log(e.response.data.detail)
        })
    },
    setMaxPage(maxPage) {
      this.maxPage = maxPage
      this.switchDisplayNextPage()
    },
    // 1つ後のデータに設定。加算後に最大ページ数に達した場合はそれ以上進めなくする。
    incrementPage() {
      this.page += 1
      this.switchDisplayPrevPage()
      this.switchDisplayNextPage()
    },
    // 1つ前のデータに設定。減算後に0未満の場合はそれ以上戻れなくする。
    decrementPage() {
      this.page -= 1
      this.switchDisplayPrevPage()
      this.switchDisplayNextPage()
    },
    switchDisplayPrevPage() {
      if (this.page <= 0) {
        this.displayPrevPage = false
      } else {
        this.displayPrevPage = true
      }
    },
    switchDisplayNextPage() {
      if (this.page >= this.maxPage - 1) {
        this.displayNextPage = false
      } else {
        this.displayNextPage = true
      }
    },
  },
}
</script>

<style scoped>
/* #prev {
  margin-top: 200px;
}
#next {
  margin-top: 200px;
} */
</style>
