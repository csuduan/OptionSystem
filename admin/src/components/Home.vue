<template>

  <div>


    <el-row class="tac" :gutter="20">
      <el-col :span="24" class="header">
        <el-col :span="3" class="logo">
          宽投期权管理系统
        </el-col>

        <el-col :span="10" class="userinfo">
          <!--<span>admin</span>
          <a href="javascript:;" @click="logout">退出</a>-->
          <el-dropdown trigger="hover">
              <span class="el-dropdown-link userinfo-inner">
                {{userName}}<i class="el-icon-arrow-down el-icon--right"></i>
              </span>
            <!--<i class="ace-icon fa fa-caret-down"></i>-->
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item>我的消息</el-dropdown-item>
              <el-dropdown-item>设置</el-dropdown-item>
              <el-dropdown-item @click.native="editFormVisible = true">修改密码</el-dropdown-item>
              <el-dropdown-item divided @click.native="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>


        </el-col>
      </el-col>
      <el-col :span="24" class="main">
        <el-col :span="3">
          <el-menu
            router :default-active="$route.path"
            default-active="/enquiryNew"
            class="el-menu-vertical-demo"
            @open="handleOpen"
            @close="handleClose">


            <el-submenu index="">
              <template slot="title">
                <i class="el-icon-menu"></i>
                <span>查询</span>
              </template>
              <el-menu-item index="/qryEnquiry">询价查询</el-menu-item>
              <el-menu-item index="/qryTrade">交易查询</el-menu-item>
              <el-menu-item index="/qryCustom">客户查询</el-menu-item>
            </el-submenu>

            <el-menu-item index="/enquiry">
              <i class="el-icon-document"></i>
              <span slot="title">询价</span>
            </el-menu-item>

            <el-menu-item index="/setting">
              <i class="el-icon-setting"></i>
              <span slot="title">系统</span>
            </el-menu-item>

            <el-menu-item index="/monitor">
              <i class="el-icon-view"></i>
              <span slot="title">监控</span>
            </el-menu-item>
          </el-menu>
        </el-col>

        <el-col :span="20">
          <router-view/>
        </el-col>
      </el-col>


    </el-row>

    <el-dialog title="修改密码" :visible.sync="editFormVisible" :close-on-click-modal="false">
      <el-form :model="ruleForm2" label-width="80px" :rules="rules2" ref="ruleForm2" label-position="left">
        <el-form-item label="新密码" prop="pass">
          <el-input type="password" v-model="ruleForm2.pass" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="checkPass">
          <el-input type="password" v-model="ruleForm2.checkPass" auto-complete="off"></el-input>
        </el-form-item>


      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click.native="submitForm('ruleForm2')">提交</el-button>
        <el-button @click.native="resetForm('ruleForm2')">取消</el-button>

      </div>
    </el-dialog>

  </div>

</template>

<script>
  import {updatePwd} from '../api/api';

  export default {
    name: 'Main',
    data() {
      var validatePass = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请输入密码'));
        } else {
          if (this.ruleForm2.checkPass !== '') {
            this.$refs.ruleForm2.validateField('checkPass');
          }
          callback();
        }
      };
      var validatePass2 = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请再次输入密码'));
        } else if (value !== this.ruleForm2.pass) {
          callback(new Error('两次输入密码不一致!'));
        } else {
          callback();
        }
      };

      return {
        userName: '',
        editFormVisible: false,
        ruleForm2: {
          pass: '',
          checkPass: '',
        },
        rules2: {
          pass: [
            {validator: validatePass, trigger: 'blur'}
          ],
          checkPass: [
            {validator: validatePass2, trigger: 'blur'}
          ],
        }
      }
    },
    watch: {
      "$route": 'checkLogin'
    },
    created() {
      this.checkLogin();
    },

    methods: {
      handleOpen(key, keyPath) {
        console.log(key, keyPath);
      },
      handleClose(key, keyPath) {
        console.log(key, keyPath);
      },
      checkLogin() {
        if (!sessionStorage.getItem('user')) {
          this.$router.push('/login');
        } else {
          this.userName = sessionStorage.getItem('user')
        }
      },
      logout: function () {
        var _this = this;
        this.$confirm('确认退出吗?', '提示', {
          //type: 'warning'
        }).then(() => {
          sessionStorage.removeItem('user');
          _this.$router.push('/login');
        }).catch(() => {

        });


      },
      submitForm(formName) {
        this.$refs[formName].validate((valid) => {
          if (valid) {
            var para = {'user': this.userName, 'pwd': this.ruleForm2.pass}
            updatePwd(para).then((res) => {

              var ret = res.data
              if (ret.code == 0) {
                this.$message({
                  message: '修改密码成功',
                  type: 'success'
                });
              }else {
                this.$message({
                  message: '修改密码失败：'+ret.msg,
                  type: 'error'
                });
              }
              this.editFormVisible=false;


            });


          } else {
            console.log('error submit!!');
            return false;
          }
        });
      },
      resetForm(formName) {
        this.$refs[formName].resetFields();
      }

    }
  }
</script>

<style scoped lang="scss">
  @import '~scss_vars';

  a {
    text-decoration: none;
    color: #fff;
  }

  .header {
    margin-bottom: 10px;
    height: 50px;
    line-height: 50px;
    //background: $color-primary;
    background: #545c64;
    color: #fff;
    .userinfo {
      text-align: right;
      padding-right: 5px;
      float: right;
      color: #fff;
      .userinfo-inner {
        font-size: 20px;
        cursor: pointer;
        color: #fff;

      }
    }
    .logo {
      //width:230px;
      height: 40px;
      font-size: 22px;
      padding-left: 20px;
      padding-right: 20px;
      //border-color: rgba(238,241,146,0.3);
      //border-right-width: 1px;
      //border-right-style: solid;
      img {
        width: 40px;
        float: left;
        margin: 10px 10px 10px 18px;
      }
      .txt {
        color: #fff;
      }
    }
    .logo-width {
      width: 230px;
    }
    .logo-collapse-width {
      width: 60px
    }
    .tools {
      padding: 0px 23px;
      width: 14px;
      height: 40px;
      line-height: 40px;
      cursor: pointer;
    }
  }

</style>
