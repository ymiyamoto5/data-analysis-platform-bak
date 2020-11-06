<template>
  <div id="analysis">
    <div id="info">
      <div id="molding_machine_name">
        <label>成形機：テスト成形機</label>
      </div>
      <div id="mold-name">
        <label>金型：テスト金型</label>
      </div>
      <div id="material_name">
        <label>材料：テスト材料</label>
      </div>
    </div>

    <div v-if="isMonitoring">
      <v-btn color="error" @click="stop">稼働停止</v-btn>
    </div>
    <div v-else>
      <v-btn color="success" @click="start">稼働開始</v-btn>
    </div>
    <v-btn color="info">設定</v-btn>

    <div id="message">
      <p>{{ this.message }}</p>
    </div>

    <v-container>
      <v-row justify="center">
        <v-dialog v-model="stopDialog" persistent max-width="400">
          <v-card>
            <v-card-title class="headline">成形の一時停止を検知しました</v-card-title>
            <v-card-text>停止理由を選択してください</v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="success" @click="finishedNormally">正常終了</v-btn>
              <v-btn color="primary" @click="pause">一時停止</v-btn>
              <v-btn color="error" @click="finishedAnomaly">異常終了</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-row>
    </v-container>

    <v-container>
      <v-row justify="center">
        <v-dialog v-model="anomalyDialog" persistent max-width="400">
          <v-card>
            <v-card-title class="headline">異常終了</v-card-title>
            <v-card-text>異常終了時の要因を選択してください</v-card-text>
              <v-container>
                <v-row justify="center">
                  <v-btn color="error" @click="selectAnomaly('バリ')">バリ</v-btn>
                  <v-btn color="error" @click="selectAnomaly('ショート')">ショート</v-btn>
                  <v-btn color="error" @click="selectAnomaly('シルバー')">シルバー</v-btn>
                </v-row>
                <v-row justify="center">
                  <v-btn color="error" @click="selectAnomaly('成形機異常')">成形機異常</v-btn>
                  <v-btn color="error" @click="selectAnomaly('金型異常')">金型異常</v-btn>
                  <v-btn color="error" @click="selectAnomaly('異音')">異音</v-btn>
                </v-row>
              </v-container>
          </v-card>
        </v-dialog>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Vue from 'vue';
import { createBaseApiClient } from '@/api/apiBase';
import { v4 as uuidv4 } from 'uuid';

export default Vue.extend({
  name: 'Analysis',
  data() {
    return {
      isMonitoring: false,
      message: "",
      eventId: "",
      stopDialog: false,
      stoppedTime: "",
      stopReason: "",
      stopFactor: "",
      anomalyDialog: false,
      isPaused: false,
    }
  },
  methods: {
    start: async function() {
      const self = this;

      self.isMonitoring = true;
      self.eventId = uuidv4();

      const requestLoop = async function() {
        const instance = createBaseApiClient()
        await instance.post("/start", {eventId: self.eventId})
        .then((res) => {
          self.message = res.data.message;
          if(self.message === "") {
            self.message = "稼働監視中..."
          }
          else {
            self.stop();
          }
        })
        .catch((e) => {
          console.log(e);
        });
      };

      const loopProcess = setInterval(() => {
        requestLoop();
        // 停止(一時停止も同じ扱い)
        if(!self.isMonitoring) {
          clearInterval(loopProcess);
        }
      }, 1000);
    },
    /**
     * [稼働終了]ボタン押下時、または監視で異常発生時に呼び出される。
     */
    stop: async function() {
      this.isMonitoring = false;
      this.stopDialog = true;
      // TODO: client timezoneの考慮
      const now = new Date();
      this.stoppedTime = now.toISOString().split('Z')[0] + '000+00:00';

      console.log('stopped.');
    },
    finishedNormally: async function() {
      this.stopReason = "正常終了";
      this.record();
      this.stopDialog = false;
      this.stopReason = "";
    },
    pause: async function() {
      this.stopReason = "一時停止";
      this.record();
      this.stopDialog = false;
      this.stopReason = "";
      this.message = "一時停止中"
    },
    finishedAnomaly: async function() {
      this.stopReason = "異常終了";
      this.stopDialog = false;
      this.anomalyDialog = true;
    },
    selectAnomaly: async function(stopFactor) {
      this.stopFactor = stopFactor;
      this.record();
      this.anomalyDialog = false;
      // 記録後は空文字に戻しておく
      this.stopFactor = "";
      this.stopReason = "";
    },
    record: async function() {
      const instance = createBaseApiClient()
      await instance
        .post("/record", {
          eventId: this.eventId,
          stoppedTime: this.stoppedTime,
          stopReason: this.stopReason,
          stopFactor: this.stopFactor,
          })
        .then((res) => {
          this.message = res.data.message;
        })
        .catch((e) => {
          console.log(e);
        });
    },
  }
});

</script>

<style scoped>
.v-btn {
  margin: 10px;
  width: 100px;
}

label {
  margin: 10px;
}

#info {
  width: 300px;
  margin: 10px;
  border: 1px solid #000000;
}
</style>
