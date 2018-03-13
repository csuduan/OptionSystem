import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import admin from '@/components/Admin'

const enquiry = resolve => require(['@/components/Enquiry'], resolve)
const trade = resolve => require(['@/components/Trade'], resolve)
const setting = resolve => require(['@/components/Setting'], resolve)

Vue.use(Router)

/* eslint-disable */
export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'admin',
      component: admin
    },
    {
      path: '/enquiry',
      name: 'enquiry',
      component: enquiry
    },

    {
      path: '/trade',
      name: 'tradeNew',
      component: trade
    },
    {
      path: '/setting',
      name: 'setting',
      component: setting
    },
  ]
})
