<template>
    <v-card flat color="transparent">
        <v-card-text>
            <v-slider
                label="特徴量"
                v-model="value"
                :max="max"
                :min="min"
                hide-details
                dense
                step="1"
                thumb-label="always"
                class="align-center"
                @input="$emit('input', $event)"
            >
            </v-slider>
        </v-card-text>
    </v-card>
</template>

<script>
export default {
    props: ['features'],
    watch: {
        features: function(new_features) {
            this.max = new_features - 1
        },
    },
    data() {
        return {
            min: 0,
            max: 10,
            value: 0,
        }
    },
}
</script>
