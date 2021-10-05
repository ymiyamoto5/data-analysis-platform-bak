<template>
    <v-app>
        <v-container class="mt-6">
            <v-row dense>
                <v-col cols="5">
                    <FeatureSelect @input="setMachine"></FeatureSelect>
                </v-col>
            </v-row>
            <v-row dense>
                <v-col cols="7">
                    <CollectDataSelect
                        @input="setTargetDir"
                        :value="machineId"
                    ></CollectDataSelect>
                </v-col>
            </v-row>
            <v-row dense>
                <v-col cols="9">
                    <ChartCard
                        :machineId="machineId"
                        :targetDir="targetDir"
                        :featureIndex="featureIndex"
                        @nof="features = $event"
                    />
                </v-col>
            </v-row>
            <v-row>
                <v-col cols="9">
                    <FeatureSelectSlider
                        v-if="dataSelected"
                        @input="setFeatureIndex"
                        :features="features"
                    ></FeatureSelectSlider>
                </v-col>
            </v-row>
            <v-row>
                <v-col cols="5">
                    <AlgorithmSelect
                        v-if="dataSelected"
                        @input="setAlgorithm"
                    ></AlgorithmSelect>
                </v-col>
            </v-row>
            <v-row dense>
                <v-col cols="9">
                    <ParameterSlider
                        v-if="algorithmSelected"
                        @input="setParameter"
                        :algorithm="algorithm"
                    ></ParameterSlider>
                </v-col>
            </v-row>
            <v-row justify="center" v-if="dataSelected">
                <v-btn
                    color="primary"
                    @click="createModel"
                    :disabled="running || !algorithmSelected"
                    :loading="running"
                    >モデル作成</v-btn
                >
            </v-row>
        </v-container>
        <v-snackbar v-model="snackbar" timeout="5000" top color="success">
            {{ snackbarMessage }}

            <template v-slot:action="{ attrs }">
                <v-btn
                    color="white"
                    text
                    v-bind="attrs"
                    @click="snackbar = false"
                >
                    Close
                </v-btn>
            </template>
        </v-snackbar>
    </v-app>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
import FeatureSelect from '@/components/CreateModel/FeatureSelect.vue'
import CollectDataSelect from '@/components/CreateModel/CollectDataSelect.vue'
import ChartCard from '@/components/CreateModel/ChartCard.vue'
import FeatureSelectSlider from '@/components/CreateModel/FeatureSelectSlider.vue'
import AlgorithmSelect from '@/components/CreateModel/AlgorithmSelect.vue'
import ParameterSlider from '@/components/CreateModel/ParameterSlider.vue'

const CREATE_MODEL_API_URL = '/api/v1/models/'

export default {
    components: {
        FeatureSelect,
        FeatureSelectSlider,
        CollectDataSelect,
        ChartCard,
        AlgorithmSelect,
        ParameterSlider,
    },
    data() {
        return {
            dataSelected: false,
            running: false,
            machineId: '',
            targetDir: '',
            collectData: '',
            featureIndex: 0,
            features: 0,
            algorithmSelected: false,
            algorithm: '',
            params: {},
            snackbar: false,
            snackbarMessage: '',
        }
    },
    methods: {
        setMachine(value) {
            this.machineId = value
        },
        setAlgorithm(value) {
            this.algorithm = value
            this.algorithmSelected = true
        },
        setTargetDir(value) {
            const targetDate = new Date(value.split('-')[0].slice(0, -1))
            this.targetDir = `${targetDate.getFullYear()}${(
                targetDate.getMonth() + 1
            )
                .toString()
                .padStart(2, '0')}${targetDate
                .getDate()
                .toString()
                .padStart(2, '0')}${targetDate
                .getHours()
                .toString()
                .padStart(2, '0')}${targetDate
                .getMinutes()
                .toString()
                .padStart(2, '0')}${targetDate
                .getSeconds()
                .toString()
                .padStart(2, '0')}`
            this.dataSelected = true
        },
        setFeatureIndex(index) {
            this.featureIndex = index
        },
        setParameter(value, key) {
            this.params[key] = value
        },
        createModel: async function() {
            this.running = true

            const postData = {
                machine_id: this.machineId,
                target_dir: this.targetDir,
                algorithm: this.algorithm,
                params: this.params,
            }
            const client = createBaseApiClient()
            await client
                .post(CREATE_MODEL_API_URL, postData)
                .then(() => {
                    this.running = false
                    this.snackbarMessage = 'モデルの作成が完了しました'
                    this.snackbar = true
                })
                .catch((e) => {
                    console.log(e.response.data.detail)
                })
        },
    },
}
</script>

<style scoped>
/* #prev {
  margin-top: 200px;
}
#next {
  margin-top: 200px;
} */
</style>
