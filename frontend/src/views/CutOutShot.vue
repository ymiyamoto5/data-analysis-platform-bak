<template>
  <div>
    <!-- <v-row>
      <v-col cols="12" sm="12" md="6" lg="4">
        <chartCard />
      </v-col>
    </v-row> -->
    <machine-select @input="setMachine"></machine-select>
    <!-- <data-select @input="setData" :value="machine"></data-select>
    <range-slider @setSliderValues="setSliderValues"></range-slider> -->
  </div>
</template>

<script>
// import chartCard from "./chart-card.vue";
// import RangeSlider from "./range-slider.vue";
import MachineSelect from '@/components/CutOutShot/MachineSelect.vue'
// import DataSelect from "./data-select.vue";
export default {
  components: {
    MachineSelect,
    // chartCard,
    // RangeSlider,
    // MachineSelect,
    // DataSelect,
  },
  data() {
    return {
      machine: '',
      lower: 0,
      upper: 0,
      data: '',
    }
  },
  methods: {
    setMachine(value) {
      console.log(value)
      this.machine = value
    },
    // setData(value) {
    //   console.log("set!!!", value);
    //   this.data = value;
    // },
    // setSliderValues(range) {
    //   this.lower = range[0];
    //   this.upper = range[1];
    // },
  },
}
</script>
