<template>
    <v-app>
        <v-tabs v-model="tab" align-with-title>
            <v-tabs-slider></v-tabs-slider>

            <v-tab v-for="item in items" :key="item">
                {{ item }}
            </v-tab>
            <v-tab :href="mlflowUri" target="_blank">
                MLflow
            </v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
            <v-tab-item>
                <CreateModel></CreateModel>
            </v-tab-item>
            <v-tab-item>
                <ServingModel></ServingModel>
            </v-tab-item>
            <v-tab-item>
                <PredictModel></PredictModel>
            </v-tab-item>
        </v-tabs-items>
    </v-app>
</template>

<script>
import CreateModel from '@/components/CreateModel.vue'
import ServingModel from '@/components/ServingModel.vue'
import PredictModel from '@/components/PredictModel.vue'

export default {
    components: {
        CreateModel,
        ServingModel,
        PredictModel,
    },
    data() {
        return {
            tab: null,
            items: ['Create Model', 'Serving Model', 'Predict Model'],
            mlflowUri: process.env.VUE_APP_MLFLOW_URL,
        }
    },
    methods: {},
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
