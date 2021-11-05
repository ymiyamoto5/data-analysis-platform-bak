<template>
    <v-container>
        <v-select
            class="select"
            :items="machines"
            label="機器"
            outlined
            dense
            @input="setMachine"
        ></v-select>
        <v-select
            class="select"
            :items="datasets"
            label="収集データ"
            outlined
            dense
            @input="setData"
        ></v-select>
        <v-select
            class="select"
            :items="shots"
            label="ショット"
            outlined
            dense
            @input="
                $emit('input', {
                    machine: machineId,
                    target: selectedDataset,
                    shot: $event,
                })
            "
        ></v-select>
    </v-container>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const DATA_LIST_API_URL = '/api/v1/features/raw/list'
const DATA_LENGTH_API_URL = '/api/v1/features/raw/length'

export default {
    data() {
        return {
            machineId: '',
            machines: [],
            dataList: [],
            datasets: [],
            selectedDataset: '',
            shots: [],
        }
    },
    mounted() {
        this.fetchDatas()
    },
    methods: {
        fetchDatas: async function() {
            const client = createBaseApiClient()
            await client
                .get(DATA_LIST_API_URL)
                .then((res) => {
                    if (res.data.length === 0) {
                        return
                    }
                    this.dataList = res.data.data
                    this.machines = this.dataList.map((x) => x[0])
                })
                .catch((e) => {
                    console.log(e.response.data.detail)
                    this.errorDialog(e.response.data.detail)
                })
        },
        setMachine(value) {
            this.machineId = value
            this.datasets = this.dataList
                .filter((x) => x[0] == value)
                .map((x) => x[1])
        },
        setData(value) {
            this.selectedDataset = value
            this.fetchDataLength()
        },
        fetchDataLength: async function() {
            const client = createBaseApiClient()
            await client
                .get(DATA_LENGTH_API_URL, {
                    params: {
                        machine_id: this.machineId,
                        target_dir: this.selectedDataset,
                    },
                })
                .then((res) => {
                    if (res.data.length === 0) {
                        return
                    }
                    this.shots = res.data.shots
                })
                .catch((e) => {
                    console.log(e.response.data.detail)
                    this.errorDialog(e.response.data.detail)
                })
        },
    },
}
</script>

<style scoped>
.select {
    width: 250px;
}
</style>
