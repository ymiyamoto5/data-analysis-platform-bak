<template>
  <v-text-field
    v-model="margin"
    :rules="[rules.required, rules.floatType]"
    label="Margin"
    outlined
    dense
    clearable
    @input="$emit('input', $event)"
  >
    <template v-slot:append-outer>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-icon v-on="on">
            mdi-help-circle-outline
          </v-icon>
        </template>
        <div>
          ショット切り出し開始後の変位値上昇に対するマージン。ショット切り出しにおいて変位値は単調減少であることを前提としているが、ノイズ等の影響で単調減少しないときのための調整パラメータ。
          <br />
          例）ショット切り出し開始しきい値を 100.0、マージン 0.0の場合、変位値が
          100.0 に到達した後にノイズサンプルで
          100.1が計測されるとショット終了とみなして切り出しが終了してしまう。
          <br />
          マージンを0.1
          に設定すると、100.1が計測されたとしてもショット切り出しを終了しない。
        </div>
      </v-tooltip>
    </template>
  </v-text-field>
</template>

<script>
export default {
  data: () => ({
    margin: 0.0,
    rules: {
      required: (value) => !!value || '必須です。',
      floatType: (value) =>
        (value >= 0.0 && value <= 10000.0) || '0.0～10000.0のみ使用可能です。',
    },
  }),
}
</script>
