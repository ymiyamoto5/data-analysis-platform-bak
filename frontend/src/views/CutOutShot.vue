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
          <StrokeDisplacementRangeSlider
            v-if="dataSelected && cutOutSensor === 'stroke_displacement'"
            @input="setStrokeDisplacementRange"
            :targetDateStr="targetDateStr"
            :maxStrokeDisplacement="maxStrokeDisplacement"
            :minStrokeDisplacement="minStrokeDisplacement"
          ></StrokeDisplacementRangeSlider>
          <ThresholdSlider
            v-if="dataSelected && cutOutSensor === 'pulse'"
            @input="setThreshold"
            :targetDateStr="targetDateStr"
          ></ThresholdSlider>
        </v-col>
        <v-col cols="9">
          <ChartCardStrokeDisplacement
            v-if="dataSelected && cutOutSensor === 'stroke_displacement'"
            :machineId="machineId"
            :targetDateStr="targetDateStr"
            :startStrokeDisplacement="startStrokeDisplacement"
            :endStrokeDisplacement="endStrokeDisplacement"
            :page="page"
            @setMaxPage="setMaxPage"
            @setMaxStrokeDisplacement="maxStrokeDisplacement = $event"
            @setMinStrokeDisplacement="minStrokeDisplacement = $event"
          />
          <ChartCardPulse
            v-if="cutOutSensor === 'pulse'"
            :machineId="machineId"
            :targetDateStr="targetDateStr"
            :threshold="threshold"
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

      <v-row v-if="dataSelected && cutOutSensor === 'stroke_displacement'">
        <v-col cols="2">
          <MarginTextField
            @input="margin = $event"
            @check="marginValidate = $event"
          ></MarginTextField>
        </v-col>
      </v-row>

      <v-row justify="center" v-if="dataSelected">
        <v-btn
          class="mb-3"
          color="primary"
          @click="start"
          :disabled="running || !marginValidate"
          :loading="running"
          >ショット切り出し開始</v-btn
        >
      </v-row>

      <v-row justify="center" v-if="running">
        <v-btn color="grey" class="mb-3 white--text" @click="beforeCancel"
          >キャンセル</v-btn
        >
      </v-row>

      <v-row justify="center" class="mr-16 ml-16 pr-16 pl-16" v-if="running">
        <v-progress-linear :value="progress" height="25">
          <strong>{{ progress }}%</strong>
        </v-progress-linear>
      </v-row>
    </v-container>
    <v-snackbar v-model="snackbar" timeout="5000" top color="success">
      {{ snackbarMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="snackbar = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import MachineSelect from '@/components/MachineSelect.vue'
import CollectDataSelect from '@/components/CutOutShot/CollectDataSelect.vue'
import ChartCardStrokeDisplacement from '@/components/CutOutShot/ChartCardStrokeDisplacement.vue'
import ChartCardPulse from '@/components/CutOutShot/ChartCardPulse.vue'
import StrokeDisplacementRangeSlider from '@/components/CutOutShot/StrokeDisplacementRangeSlider.vue'
import ThresholdSlider from '@/components/CutOutShot/ThresholdSlider.vue'
import MarginTextField from '@/components/CutOutShot/MarginTextField.vue'

const TARGET_DIR_API_URL = '/api/v1/cut_out_shot/target_dir'
const CUT_OUT_SENSOR_FROM_HISTORY_API_URL =
  '/api/v1/cut_out_shot/cut_out_sensor_from_history'
const CUT_OUT_SHOT_DISPLACEMENT_API_URL =
  '/api/v1/cut_out_shot/stroke_displacement'
const CUT_OUT_SHOT_PULSE_API_URL = '/api/v1/cut_out_shot/pulse'
const CUT_OUT_SHOT_CANCEL_API_URL = '/api/v1/cut_out_shot/cancel'
const CUT_OUT_SHOT_TASK = '/api/v1/celery_tasks/'

export default {
  components: {
    MachineSelect,
    StrokeDisplacementRangeSlider,
    ThresholdSlider,
    CollectDataSelect,
    ChartCardStrokeDisplacement,
    ChartCardPulse,
    MarginTextField,
  },
  data() {
    return {
      dataSelected: false,
      running: false,
      page: 0, // グラフの表示ファイル
      maxPage: 0, // グラフの最大ページング数（対象データのファイル数）
      displayPrevPage: false, // グラフを前に戻せるか
      displayNextPage: false, // グラフを先に進められるか
      machineId: '',
      targetDateStr: '', // yyyyMMdd文字列
      cutOutSensor: '', // 切り出し対象となるセンサー種（ストローク変位またはパルス）
      startStrokeDisplacement: 0, // ストローク変位センサーで切り出す場合のショット開始ストローク変位値
      endStrokeDisplacement: 0, // ストローク変位センサーで切り出す場合のショット終了ストローク変位値
      threshold: 0, // パルスで切り出す場合のしきい値
      collectData: '', // データ収集開始日時 - 終了日時文字列
      margin: '0.0',
      marginValidate: true,
      maxStrokeDisplacement: 0, // ストローク変位しきい値の最大値
      minStrokeDisplacement: 0, // ストローク変位しきい値の最小値
      snackbar: false,
      snackbarMessage: '',
      progress: 0, // タスクの進捗
    }
  },
  methods: {
    confirmDialog(message, callback) {
      this.$store.commit('setShowConfirmDialog', true)
      this.$store.commit('setConfirmMsg', message)
      this.$store.commit('setCallbackFunc', callback)
    },
    errorSnackbar(message) {
      this.$store.commit('setShowErrorSnackbar', true)
      this.$store.commit('setErrorHeader', message.statusText)
      this.$store.commit('setErrorMsg', message.data.detail)
    },
    setMachine(value) {
      this.dataSelected = false
      this.targetDateStr = ''
      this.cutOutSensor = ''
      this.machineId = value
    },
    setCollectData(value) {
      this.collectData = value
      this.dataSelected = true
      this.targetDateStr = ''
      this.cutOutSensor = ''
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
          // 切り出し対象センサー特定
          this.fetchCutOutSensorFromHistory()
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    // 切り出しの基準となるセンサー特定
    fetchCutOutSensorFromHistory: async function() {
      const client = createBaseApiClient()
      await client
        .get(CUT_OUT_SENSOR_FROM_HISTORY_API_URL, {
          params: {
            machine_id: this.machineId,
            target_date_str: this.targetDateStr,
          },
        })
        .then((res) => {
          if (res.data === null) {
            return
          }
          this.cutOutSensor = res.data.cut_out_sensor
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },

    setStrokeDisplacementRange(range) {
      this.startStrokeDisplacement = range[1]
      this.endStrokeDisplacement = range[0]
    },

    setThreshold(value) {
      this.threshold = value
    },

    // ショット切り出し開始
    start: async function() {
      this.running = true

      let url = ''
      let postData = {}
      if (this.cutOutSensor === 'stroke_displacement') {
        url = CUT_OUT_SHOT_DISPLACEMENT_API_URL
        postData = {
          machine_id: this.machineId,
          start_stroke_displacement: this.startStrokeDisplacement,
          end_stroke_displacement: this.endStrokeDisplacement,
          target_date_str: this.targetDateStr,
          margin: this.margin,
        }
      } else if (this.cutOutSensor === 'pulse') {
        url = CUT_OUT_SHOT_PULSE_API_URL
        postData = {
          machine_id: this.machineId,
          threshold: this.threshold,
          target_date_str: this.targetDateStr,
        }
      }

      const client = createBaseApiClient()
      await client
        .post(url, postData)
        .then((res) => {
          // NOTE: setIntervalでthisのコンテキストが変わってしまうため、thatに退避（もっと良い方法があるかも）
          const that = this
          // 3秒置きにタスクステータスをチェックし、成功または失敗するまでループ
          const intervalId = setInterval(async function() {
            const pollingClinet = createBaseApiClient()
            await pollingClinet
              .get(CUT_OUT_SHOT_TASK + res.data.task_id)
              .then((res) => {
                const taskStatus = res.data.status
                console.log(taskStatus)
                if (taskStatus === 'SUCCESS') {
                  that.running = false
                  that.progress = 0
                  that.snackbarMessage = 'ショット切り出しが完了しました'
                  that.snackbar = true
                  clearInterval(intervalId)
                } else if (taskStatus === 'FAILURE') {
                  that.running = false
                  that.progress = 0
                  that.errorSnackbar('ショット切り出しが失敗しました')
                  clearInterval(intervalId)
                } else if (taskStatus === 'PROGRESS') {
                  that.progress = res.data.result.progress
                } else if (taskStatus === 'REVOKED') {
                  clearInterval(intervalId)
                }
              })
              .catch((e) => {
                that.running = false
                console.log(e.response.data.detail)
                that.errorSnackbar(e.response)
              })
          }, 3000)
        })
        .catch((e) => {
          this.running = false
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
        })
    },
    // ショット切り出し停止
    beforeCancel() {
      this.confirmDialog('停止してもよいですか？', this.cancel)
    },
    cancel: async function() {
      const client = createBaseApiClient()
      await client
        .get(CUT_OUT_SHOT_CANCEL_API_URL, {
          params: {
            machine_id: this.machineId,
          },
        })
        .then(() => {
          this.running = false
          this.progress = 0
          this.snackbarMessage = 'ショット切り出しをキャンセルしました'
          this.snackbar = true
        })
        .catch((e) => {
          console.log(e.response.data.detail)
          this.errorSnackbar(e.response)
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
.v-btn {
  width: 180px;
}
</style>
