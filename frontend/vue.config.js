module.exports = {
  configureWebpack: {
    devtool: 'source-map',
  },
  assetsDir: 'static',
  transpileDependencies: ['vuetify'],
  devServer: {
    host: 'localhost',
    port: 8080,
  },
}
