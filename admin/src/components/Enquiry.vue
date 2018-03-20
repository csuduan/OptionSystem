<template>


  <el-row class="tac" :gutter="20">
    <el-col :span="6">
      <el-form ref="myform" :model="myform" :rules="rules" label-width="80px" label-position="left">
        <el-form-item label="股票代码" prop="stock">
          <el-input v-model="myform.stock" auto-complete="on"></el-input>
        </el-form-item>
        <el-form-item label="期限" prop="period">
          <el-input v-model="myform.period" auto-complete="on"></el-input>
        </el-form-item>
        <el-form-item label="名义本金" prop="amount">
          <el-input-number v-model="myform.amount" auto-complete="off"></el-input-number>
        </el-form-item>
        <el-form-item label="执行比例" prop="strikePct">
          <el-input-number v-model="myform.strikePct" auto-complete="off"></el-input-number>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSubmit">询价</el-button>
          <el-button @click="resetForm('myform')">重置</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <!--<el-col :span="8" :offset="3">
      <el-input
        type="textarea"
        :rows="13"
        placeholder="等待询价结果..."
        v-model="textarea">
      </el-input>
    </el-col>-->

    <el-col :span="6" :offset="3">
      <el-form ref="myresult" :model="myresult" :rules="myresultrules" label-width="80px" label-position="left">

        <el-form-item label="询价时间">
          <el-input v-model="myresult.time" auto-complete="off" disabled></el-input>
        </el-form-item>
        <el-form-item label="询价编号" prop="No">
          <el-input v-model="myresult.No" auto-complete="off" disabled></el-input>
        </el-form-item>
        <el-form-item label="期权费">
          <el-input-number v-model="myresult.cost" auto-complete="off" disabled></el-input-number>
        </el-form-item>


        <el-form-item label="客户名称" prop="custom">
          <el-input v-model="myresult.custom" auto-complete="off"></el-input>
        </el-form-item>

        <el-form-item label="名义本金" prop="maxAmount">
          <el-input-number v-model="myresult.maxAmount" auto-complete="off"></el-input-number>
          <el-button type="primary" @click="order" style="float: right">下单</el-button>
        </el-form-item>


      </el-form>

    </el-col>

  </el-row>

</template>

<script>
  import {enquiry,trade} from '../api/api';


  export default {
    name: "enquiry-oper",
    data() {
      return {
        textarea: '',

        myresult: {
          No: '',
          cost: '',
          maxAmount: '',
          time: '',
          custom: ''

        },

        myresultrules: {

          No: [
            {required: true, message: '询价编号不能为空', trigger: 'blur'},
          ],
          maxAmount: [
            {required: true, message: '名义本金不能为空', trigger: 'blur'},
          ],
          custom: [
            {required: true, message: '客户编号不能为空', trigger: 'blur'},
          ],
        },

        myform: {
          stock: '',
          period: '',
          amount: 0,
          strikePct: 1
        },
        rules: {

          stock: [
            {required: true, message: '请输入股票代码', trigger: 'blur'},
            {min: 9, max: 9, message: '长度必须为9', trigger: 'blur'}
          ],
          period: [
            {required: true, message: '请输入期限', trigger: 'blur'},
            {min: 2, max: 3, message: '长度必须为2-3为，如1M', trigger: 'blur'}
          ],
          amount: [
            {type: 'number', message: '名义本金必须为数字', trigger: 'blur'}
          ],
          strikePct: [
            {type: 'number', message: '行权比例必须为数字', trigger: 'blur'}
          ]

        },


      }
    },
    methods: {
      onSubmit() {
        console.log('submit!');
        this.textarea = ''
        this.$refs.myform.validate((valid) => {
          if (!valid) {
            return false;
          } else {
            //验证通过

            enquiry(this.myform).then((res) => {
              var data = res.data
              this.textarea = JSON.stringify(res.data);
              if (data['errCode'] != 0) {
                this.$message({
                  showClose: true,
                  message: data['errMsg'],
                  type: 'error'
                })
              } else {
                this.myresult = Object.assign({}, data['data']);
              }


              //NProgress.done();
            });

          }
        });


      },
      resetForm(formName) {
        this.$refs[formName].resetFields();
      },
      order() {

        this.$refs.myresult.validate((valid) => {
          if (!valid) {
            return false;
          }else {
            var param={
              'enquiryNo':this.myresult.No,
              'custom':this.myresult.custom,
              'amount':this.myresult.maxAmount
            }

            trade(param).then((res) => {
              var data = res.data
              this.textarea = JSON.stringify(res.data);
              if (data['errCode'] != 0) {
                this.$message({
                  showClose: true,
                  message: data['errMsg'],
                  type: 'error'
                })
              } else {
                this.$message({
                  showClose: true,
                  message: '下单成功，交易编号：'+data['data'].tradeNo,
                  type: 'success'
                })
              }


              //NProgress.done();
            });



          }
        })
      }
    }
  }
</script>

<style scoped>

</style>
