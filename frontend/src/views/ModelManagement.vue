<template>
    <v-app>
        <v-tabs v-model="tab" align-with-title>
            <v-tabs-slider></v-tabs-slider>

            <v-tab v-for="item in items" :key="item">
                {{ item }}
            </v-tab>
            <v-tab href="http://10.3.18.117:5000" target="_blank">
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
        </v-tabs-items>
    </v-app>
</template>

<script>
import CreateModel from '@/components/CreateModel.vue'
import ServingModel from '@/components/ServingModel.vue'

export default {
    components: {
        CreateModel,
        ServingModel,
    },
    data() {
        return {
            tab: null,
            items: ['Create Model', 'Serving Model'],
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
