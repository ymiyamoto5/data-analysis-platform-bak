<template>
    <v-expansion-panels>
        <v-expansion-panel
            v-for="(container, index) in attribute"
            :key="container.image"
            class="mb-3"
        >
            <v-expansion-panel-header>
                <v-row no-gutters>
                    <v-col cols="8">
                        {{ container.image }}
                    </v-col>
                </v-row>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
                <v-row>
                    <v-col cols="4">
                        <v-text-field
                            label="ポート番号"
                            type="number"
                            :rules="rules"
                            @input="setPortNumber(index, $event)"
                        ></v-text-field>
                    </v-col>
                </v-row>
                <v-row class="mb-3">
                    <v-btn
                        :color="container.color"
                        class="mr-3"
                        @click="containerStateChange(index)"
                    >
                        {{ container.label }}
                    </v-btn>
                    <v-btn
                        v-if="container.delete"
                        color="error"
                        @click="deleteContainer(index)"
                    >
                        削除
                    </v-btn>
                </v-row>
            </v-expansion-panel-content>
        </v-expansion-panel>
    </v-expansion-panels>
</template>

<script>
import { createBaseApiClient } from '@/api/apiBase'
const CONTAINER_API_URL = '/api/v1/models/container/'
const CONTAINER_RUN_API_URL = CONTAINER_API_URL + 'run/'
const CONTAINER_STOP_API_URL = CONTAINER_API_URL + 'stop/'

export default {
    props: ['containers'],
    data() {
        return {
            portNumber: [],
            attribute: this.containers.map(this.makeAttribute),
            rules: [(value) => !!value || '必須項目'],
        }
    },
    watch: {
        containers: function(newContainers) {
            this.attribute = newContainers.map(this.makeAttribute)
        },
    },
    methods: {
        makeAttribute(container) {
            return {
                image: container.image,
                state: container.state,
                name: container.name,
                color: container.state == 'stopping' ? 'primary' : 'error',
                label: container.state == 'stopping' ? '起動' : '停止',
                delete: container.state == 'stopping' ? true : false,
            }
        },
        setButtonLabel(container) {
            return container.state == 'stopping' ? '起動' : '停止'
        },
        setButtonColor(container) {
            return container.state == 'stopping' ? 'primary' : 'error'
        },
        setPortNumber(index, value) {
            this.portNumber[index] = value
        },
        containerStateChange: async function(index) {
            let request = ''
            if (this.containers[index].state == 'stopping') {
                request =
                    CONTAINER_RUN_API_URL +
                    this.containers[index].image +
                    '/' +
                    this.portNumber[index]
            } else {
                request = CONTAINER_STOP_API_URL + this.containers[index].name
            }

            const client = createBaseApiClient()
            await client
                .put(request)
                .then((res) => {
                    if (res.data.length === 0) {
                        return
                    }
                    this.containers[index] = res.data.data
                    this.attribute = this.containers.map(this.makeAttribute)
                })
                .catch((e) => {
                    console.log(e.response)
                })
        },
        deleteContainer: async function(index) {
            const client = createBaseApiClient()
            await client
                .delete(CONTAINER_API_URL + this.containers[index].image)
                .then((res) => {
                    if (res.data.length === 0) {
                        return
                    }
                    this.containers.splice(index, 1)
                })
                .catch((e) => {
                    console.log(e.response)
                    this.errorDialog(e.response)
                })
        },
    },
}
</script>
