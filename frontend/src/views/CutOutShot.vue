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
          ></DisplacementRangeSlider>
        </v-col>
        <v-col cols="11">
          <ChartCard :machine_id="machine_id" :collectData="collectData" />
        </v-col>
      </v-row>
      <v-row justify="center" v-if="dataSelected">
        <v-btn color="primary" @click="start">ショット切り出し開始</v-btn>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
import MachineSelect from '@/components/CutOutShot/MachineSelect.vue'
import CollectDataSelect from '@/components/CutOutShot/CollectDataSelect.vue'
import ChartCard from '@/components/CutOutShot/ChartCard.vue'
import DisplacementRangeSlider from '@/components/CutOutShot/DisplacementRangeSlider.vue'

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
      machine_id: '',
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
    },
    setDisplacementRange(range) {
      console.log(range)
      this.start_displacement = range[1]
      this.end_displacement = range[0]
    },
    start: async function() {
      this.started = true
    },
  },
}
</script>

<style scoped></style>
