<template>
  <div id="machines">
    <v-simple-table>
      <thead>
        <tr>
          <th v-for="item in Object.keys(tableHeader)" :key="item">
            {{ tableHeader[item] }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="machine in machines" :key="machine.machine_id">
          <td>{{ machine.machine_name }}</td>
          <td>
            <ul>
              <li v-for="gateway in machine.gateways" :key="gateway.gateway_id">
                {{ gateway.gateway_id }}
              </li>
            </ul>
          </td>
          <td>
            <ul>
              <template v-for="gateway in machine.gateways">
                <li
                  v-for="handler in gateway.handlers"
                  :key="handler.handler_id"
                >
                  {{ handler.handler_id }}
                </li>
              </template>
            </ul>
          </td>
          <td>
            <ul>
              <template v-for="gateway in machine.gateways">
                <template v-for="handler in gateway.handlers">
                  <li v-for="sensor in handler.sensors" :key="sensor.sensor_id">
                    {{ sensor.sensor_name }}
                  </li>
                </template>
              </template>
            </ul>
          </td>
          <td>
            <ul>
              <template v-for="gateway in machine.gateways">
                <v-chip
                  :color="getColor(gateway.status)"
                  :key="gateway.gateway_id"
                >
                  {{ gateway.status }}
                </v-chip>
              </template>
            </ul>
          </td>
        </tr>
      </tbody>
    </v-simple-table>
  </div>

  <!-- <v-data-table :headers="headers" :items="machines" class="elevation-1">
    <template v-slot:item.machine="{ item }">
      <v-chip :color="getColor(item.calories)" dark>
        {{ item.calories }}
      </v-chip>
    </template>
  </v-data-table> -->
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'

const API_URL = '/api/v1/machines'

export default {
  name: 'data-collect',
  data() {
    return {
      tableHeader: {
        machine_name: '機器',
        gateway_id: 'ゲートウェイID',
        handler_id: 'ハンドラーID',
        sensor_name: 'センサー',
        status: '状態',
      },
      machines: [],
    }
  },
  created: function() {
    this.fetchTableData()
  },
  methods: {
    getColor(stauts) {
      if (stauts === 'stop') return 'red'
      else return 'green'
    },
    fetchTableData: async function() {
      const client = createBaseApiClient()
      let data = []
      await client
        .get(API_URL)
        .then((res) => {
          if (res.data.length === 0) {
            return
          }
          data = res.data
          console.log(data)
          this.machines = data
        })
        .catch(() => {
          console.log('error')
        })
    },
  },
}
</script>

<style scoped>
ul {
  list-style: none;
}
</style>
