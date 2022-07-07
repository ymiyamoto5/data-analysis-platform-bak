module.exports = {
  configureWebpack: {
    devtool: 'source-map',
  },
  // outputDir: '../backend/app/dist',
  assetsDir: 'static',
  transpileDependencies: ['vuetify'],
  devServer: {
    host: process.env.VUE_DEV_SERVER_IP,
    port: process.env.VUE_DEV_SERVER_PORT,
  },
}
