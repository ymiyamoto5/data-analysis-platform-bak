<template>
  <div>
    <MachineSelect @input="setMachine"></MachineSelect>
    <CollectDataSelect
      @input="setCollectData"
      :value="machine"
    ></CollectDataSelect>
    <v-row>
      <v-col cols="12" sm="12" md="6" lg="4">
        <ChartCard />
      </v-col>
    </v-row>
    <!-- <range-slider @setSliderValues="setSliderValues"></range-slider> -->
  </div>
</template>

<script>
// import RangeSlider from "./range-slider.vue";
import MachineSelect from '@/components/CutOutShot/MachineSelect.vue'
import CollectDataSelect from '@/components/CutOutShot/CollectDataSelect.vue'
import ChartCard from '@/components/CutOutShot/ChartCard.vue'

export default {
  components: {
    MachineSelect,
    // RangeSlider,
    CollectDataSelect,
    ChartCard,
  },
  data() {
    return {
      machine: '',
      lower: 0,
      upper: 0,
      collectData: '',
    }
  },
  methods: {
    setMachine(value) {
      this.machine = value
    },
    setCollectData(value) {
      console.log('set!!!', value)
      this.collectData = value
    },
    // setSliderValues(range) {
    //   this.lower = range[0];
    //   this.upper = range[1];
    // },
  },
}
</script>
