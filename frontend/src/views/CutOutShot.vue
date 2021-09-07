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
          ></DisplacementRangeSlider>
        </v-col>
        <v-col cols="11">
          <ChartCard :machineId="machineId" :collectData="collectData" />
        </v-col>
      </v-row>
      <v-row justify="center" v-if="dataSelected">
        <v-btn color="primary">ショット切り出し開始</v-btn>
      </v-row>
      <v-row justify="center" v-if="started">
        <v-textarea></v-textarea>
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
      machineId: '',
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
    },
    setDisplacementRange(range) {
      console.log(range)
      this.startDisplacement = range[1]
      this.endDisplacement = range[0]
    },
  },
}
</script>

<style scoped></style>
