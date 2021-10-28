module.exports = {
  configureWebpack: {
    devtool: 'source-map',
  },
  outputDir: '../backend/app/dist',
  assetsDir: 'static',
  transpileDependencies: ['vuetify'],
  devServer: {
    host: 'localhost',
    port: 8080,
  },
}
