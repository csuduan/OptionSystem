import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import admin from '@/components/Admin'

const enquiry = resolve => require(['@/components/Enquiry'], resolve)
const qryEnquiry = resolve => require(['@/components/QryEnquiry'], resolve)
const qryTrade = resolve => require(['@/components/QryTrade'], resolve)
const setting = resolve => require(['@/components/Setting'], resolve)
const monitor = resolve => require(['@/components/Monitor'], resolve)

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
      path: '/qryEnquiry',
      name: 'qryEnquiry',
      component: qryEnquiry
    },

    {
      path: '/qryTrade',
      name: 'qryTrade',
      component: qryTrade
    },
    {
      path: '/setting',
      name: 'setting',
      component: setting
    },
    {
      path: '/monitor',
      name: 'monitor',
      component: monitor
    },
  ]
})
