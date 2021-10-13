<template>
    <v-container>
        <v-select
            class="select"
            :items="models"
            label="モデル"
            outlined
            dense
            @input="setModel"
        ></v-select>
        <v-select
            class="select"
            v-model="selectedVersion"
            :items="versions"
            label="バージョン"
            outlined
            dense
            @change="
                $emit('selectInput', { model: selectedModel, version: $event })
            "
        ></v-select>
        <v-text-field
            label="コンテナ名"
            counter="128"
            :rules="rules"
            hide-details="auto"
            outlined
            dense
            @input="$emit('textInput', $event)"
        ></v-text-field>
    </v-container>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const MODELS_API_URL = '/api/v1/models/'
const MODEL_VERSIONS_API_URL = '/api/v1/models/versions'

export default {
    data() {
        return {
            models: [],
            versions: [],
            selectedModel: '',
            selectedVersion: '',
            rules: [
                (value) => !!value || '必須項目',
                (value) => (value && value.length <= 128) || '無効な文字列長',
                (value) => /^[\w][\w.-]*$/.test(value) || '無効なコンテナ名',
            ],
        }
    },
    watch: {
        selectedModel: function() {
            this.fetchVersions()
        },
    },
    mounted() {
        this.fetchModels()
    },
    methods: {
        fetchModels: async function() {
            const client = createBaseApiClient()
            await client
                .get(MODELS_API_URL)
                .then((res) => {
                    if (res.data.length === 0) {
                        return
                    }
                    this.models = res.data
                })
                .catch((e) => {
                    console.log(e.response.data.detail)
                    this.errorDialog(e.response.data.detail)
                })
        },
        setModel(model) {
            this.selectedModel = model
        },
        fetchVersions: async function() {
            const client = createBaseApiClient()
            await client
                .get(MODEL_VERSIONS_API_URL, {
                    params: { model: this.selectedModel },
                })
                .then((res) => {
                    if (res.data.length === 0) {
                        return
                    }
                    this.selectedVersion = ''
                    this.$emit('selectInput', {
                        model: this.selectedModel,
                        version: '',
                    })
                    this.versions = res.data
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
