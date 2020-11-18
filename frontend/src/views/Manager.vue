<template>
  <div id="manager">
    <v-container>
      <v-row justify="space-around">
        <v-col>
          <div v-if="isMonitoring">
            <v-btn color="error" @click="stop">稼働停止</v-btn>
          </div>
          <div v-else>
            <v-btn color="success" @click="start">稼働開始</v-btn>
          </div>
        </v-col>
        <v-col>
          <v-btn color="info">設定</v-btn>
        </v-col>
      </v-row>
    </v-container>

    <v-dialog v-model="stopDialog" fullscreen hide-overlay>
      <v-card>
        <v-toolbar dark color="primary">
          <v-toolbar-title>
            成形の一時停止を検知しました。停止理由を選択してください。
          </v-toolbar-title>
        </v-toolbar>
        <v-card-actions>
          <v-container>
            <v-row justify="space-around">
              <v-col>
                <v-btn color="success" @click="finishedNormally">正常終了</v-btn>
              </v-col>
              <v-col>
                <v-btn color="primary" @click="pause">一時停止</v-btn>
              </v-col>
              <v-col>
                <v-btn color="error" @click="finishedAnomaly">異常終了</v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="normallyDialog" fullscreen hide-overlay>
      <v-card>
        <v-toolbar dark color="primary">
          <v-toolbar-title>要因を選択してください</v-toolbar-title>
        </v-toolbar>
        <v-container>
          <v-row justify="space-around">
            <v-col v-for="item in stopFactorsNormally" :key="item.id">
              <v-btn color="success" @click="selectStopFactor(item.name)">{{item.name}}</v-btn>
            </v-col>
          </v-row>
        </v-container>
      </v-card>
    </v-dialog>

    <v-dialog v-model="anomalyDialog" fullscreen hide-overlay>
      <v-card>
        <v-toolbar dark color="primary">
          <v-toolbar-title>要因を選択してください</v-toolbar-title>
        </v-toolbar>
        <v-container>
          <v-row justify="space-around">
            <v-col v-for="item in stopFactorsAnomaly" :key="item.id">
              <v-btn color="error" @click="selectStopFactor(item.name)">{{item.name}}</v-btn>
            </v-col>
          </v-row>
        </v-container>
      </v-card>
    </v-dialog>

  </div>
</template>

<script>
import Vue from 'vue';
import { createBaseApiClient } from '@/api/apiBase';
import { v4 as uuidv4 } from 'uuid';

export default Vue.extend({
  name: 'Manager',
  data() {
    return {
      isMonitoring: false,
      message: "",
      eventId: "",
      stopDialog: false,
      stoppedTime: "",
      stopReason: "",
      stopFactor: "",
      normallyDialog: false,
      anomalyDialog: false,
      isPaused: false,
      stopFactorsNormally: [
        {id: 0, name: "日常点検"},
        {id: 1, name: "部品交換・定期点検"},
        {id: 2, name: "ロット段取"},
        {id: 3, name: "品種段取"},
        {id: 4, name: "シフト段取"},
        {id: 5, name: "材料交換段取"},
        {id: 6, name: "その他段取"},
        {id: 7, name: "ラインアンバランス"},
        {id: 8, name: "その他設備干渉"},
        {id: 9, name: "製品検査"},
        {id: 10, name: "品質点検"},
      ],
      stopFactorsAnomaly: [
        {id: 0, name: "バリ"},
        {id: 1, name: "ショート"},
        {id: 2, name: "シルバー"},
        {id: 3, name: "成形機異常"},
        {id: 4, name: "金型異常"},
        {id: 5, name: "異音"},
      ]
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
          console.log(self.message);
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
      this.stopDialog = false;
      this.normallyDialog = true;
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
    selectStopFactor: async function(stopFactor) {
      this.stopFactor = stopFactor;
      this.record();
      this.normallyDialog = false;
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
  margin: 2vw;
  width: 20vw;
  min-width: 10vw;
  height: 100px;
  min-height: 100px;
}

.v-btn.v-size--default {
    font-size: 2vw;
}
</style>
