var path = require('path')
function resolve(dir) {
  return path.join(__dirname,  dir)
}

module.exports = {
    devtool: 'eval-source-map',

  //打包入口，非路由
  entry: {
      'app':resolve('src/views/index.js')
  },
    output: {
    path: __dirname + "/public",
    filename: "bundle.js"
  }
}
