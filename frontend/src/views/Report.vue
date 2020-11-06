<template>
  <v-container>
    <v-row>
      <v-col cols="10">
        <v-data-table :headers="headers" :items="serverDatas" :sort-by.sync="sortBy" :sort-desc.sync="sortDesc">
          <template v-slot:[`item.start_time`]="{ item }">
            <span>{{ new Date(item.start_time).toLocaleString() }}</span>
          </template>
          <template v-slot:[`item.end_time`]="{ item }">
            <span>{{ new Date(item.end_time).toLocaleString() }}</span>
          </template>
          <template v-slot:[`item.stop_reason`]="{ item }">
            <v-chip :color=getColor(item.stop_reason) dark>{{ item.stop_reason }}</v-chip>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase';

export default {
  data() {
    return {
      headers: [
        {
          text: "開始時刻",
          value: "start_time",
        },
        { 
          text: "終了時刻",
          value: "end_time"
        },
        {
          text: "成形機名",
          value: "molding_machine_name",
          sortable: false,
        },
        {
          text: "金型名",
          value: "mold_name",
          sortable: false,
        },
        {
          text: "材料名",
          value: "material_name",
          sortable: false,
        },
        {
          text: "停止理由",
          value: "stop_reason",
        },
        {
          text: "停止要因",
          value: "stop_factor",
        },
      ],
      sortBy: 'start_time',
      sortDesc: true,
      serverDatas: [],
    };
  },

  methods: {
    getColor(stopReason) {
      if (stopReason === "正常終了")
        return "green";
      if (stopReason === "異常終了")
        return "red";
      if (stopReason === "一時停止")
        return "blue";
      return "gray"
    }
  },
  mounted() {
    const instance = createBaseApiClient()
    instance
      .get("/report")
      .then((res) => {
        this.serverDatas = res.data;
      })
      .catch((e) => {
        console.log(e);
      });
  },
};
</script>