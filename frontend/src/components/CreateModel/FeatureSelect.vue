<template>
    <v-container>
        <v-select
            class="select"
            :items="machines"
            label="特徴量"
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
            @input="$emit('input', [selectedMachine, $event])"
        ></v-select>
    </v-container>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const FEATURES_LIST_API_URL = '/api/v1/features/list'

export default {
    data() {
        return {
            features: [],
            machines: [],
            selectedMachine: '',
            datasets: [],
        }
    },
    mounted() {
        this.fetchFeatures()
    },
    methods: {
        fetchFeatures: async function() {
            const client = createBaseApiClient()
            await client
                .get(FEATURES_LIST_API_URL)
                .then((res) => {
                    if (res.data.length === 0) {
                        return
                    }
                    this.features = res.data.data
                    this.machines = this.features.map((x) => x[0])
                })
                .catch((e) => {
                    console.log(e.response.data.detail)
                    this.errorDialog(e.response.data.detail)
                })
        },
        setMachine(value) {
            this.selectedMachine = value
            this.datasets = this.features
                .filter((x) => x[0] == value)
                .map((x) => x[1])
        },
    },
}
</script>

<style scoped>
.select {
    width: 250px;
}
</style>
