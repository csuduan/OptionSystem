import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import admin from '@/components/Admin'

const enquiry = resolve => require(['@/components/Enquiry'], resolve)
const qryEnquiry = resolve => require(['@/components/QryEnquiry'], resolve)
const qryTrade = resolve => require(['@/components/QryTrade'], resolve)
const setting = resolve => require(['@/components/Setting'], resolve)
const monitor = resolve => require(['@/components/Monitor'], resolve)
const Login = resolve => require(['@/components/Login'], resolve)
const Home = resolve => require(['@/components/Home'], resolve)
const qryCustom=resolve => require(['@/components/QryCustom'], resolve)

Vue.use(Router)

/* eslint-disable */
export default new Router({
  mode: 'history',
  routes: [
/*    {
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
    },*/


    {
      path: '/login',
      component: Login,
      name: 'login',
    },
    {
      path: '/',
      component: Home,
      name: '',
      children: [
        {path: '/enquiry', component: enquiry, name: 'enquiry'},
        {path: '/qryEnquiry', component: qryEnquiry, name: 'qryEnquiry'},
        {path: '/qryTrade', component: qryTrade, name: 'qryTrade'},
        {path: '/qryCustom', component: qryCustom, name: 'qryCustom'},
        {path: '/setting', component: setting, name: 'setting'},
        {path: '/monitor', component: monitor, name: 'monitor'},
      ]
    },

  ]
})
