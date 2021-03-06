// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import Mock from './mock'
import 'font-awesome/css/font-awesome.min.css'

/*import VueWebsocket from "vue-websocket";
Vue.use(VueWebsocket,"ws://127.0.0.1:5000",);*/


Vue.config.productionTip = false

Vue.use(ElementUI)

//Mock.bootstrap();

/* eslint-disable no-new */
var vm=new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
