<template>
  <div id="app">

    <el-row class="tac" :gutter="20">
      <el-col :span="3">
        <el-menu
          router :default-active="$route.path"
          default-active="/enquiryNew"
          class="el-menu-vertical-demo"
          @open="handleOpen"
          @close="handleClose">
          <el-menu-item index="/enquiry" >
            <i class="el-icon-menu"></i>
            <span slot="title">询价</span>

          </el-menu-item>
          <el-menu-item index="/trade" >
            <i class="el-icon-document"></i>
            <span slot="title">交易</span>
          </el-menu-item>

          <el-menu-item index="/setting">
            <i class="el-icon-setting"></i>
            <span slot="title">系统</span>
          </el-menu-item>
        </el-menu>
      </el-col>

      <el-col :span="20">
        <router-view/>
      </el-col>
    </el-row>
  </div>
</template>

<script>
  export default {
    name: 'App',

    methods: {
      handleOpen(key, keyPath) {
        console.log(key, keyPath);
      },
      handleClose(key, keyPath) {
        console.log(key, keyPath);
      }
    }
  }
</script>

<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    margin-top: 60px;
  }
  .toolbar{
    padding:10px;
    margin: 10px 0px;
  }
</style>
