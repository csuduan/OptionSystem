<template>
  <section>
    <el-col :span="24" style="padding-bottom: 0px;">
      <el-form :inline="true" :model="filters">
        <el-form-item>
          <el-input v-model="filters.custom" placeholder="客户" clearable></el-input>
        </el-form-item>
        <el-form-item>
          <el-date-picker type="date" placeholder="交易日" v-model="filters.tradingDay" value-format="yyyyMMdd"></el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.status" placeholder="状态" clearable>
            <el-option value="UnTraded" label="未成交"></el-option>
            <el-option value="Traded" label="已成交"></el-option>
            <el-option value="Refused" label="已拒绝"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getTrades" icon="el-icon-search">查询</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <!--列表-->
    <el-table :data="trades" highlight-current-row v-loading="listLoading" @selection-change="selsChange"
              style="width: 100%;">
      <el-table-column type="selection" width="55">
      </el-table-column>
      <el-table-column prop="tradeNo" label="编号" width="80" sortable>
      </el-table-column>
      <el-table-column prop="custom" label="客户" width="120" sortable>
      </el-table-column>
      <el-table-column prop="tradingDay" label="交易日" width="100" sortable>
      </el-table-column>
      <el-table-column prop="code" label="股票" width="100" sortable>
      </el-table-column>
      <el-table-column prop="period" label="期限" width="80" sortable>
      </el-table-column>
      <el-table-column prop="strikePct" label="行权比例" width="100" sortable>
      </el-table-column>
      <el-table-column prop="amount" label="金额" min-width="80" sortable>
      </el-table-column>
      <el-table-column prop="insertTms" label="下单时间" min-width="150" sortable>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="90" sortable>
      </el-table-column>
      <el-table-column prop="tradePrice" label="成交价格" min-width="100" sortable>
      </el-table-column>
      <el-table-column prop="tradeTms" label="成交时间" min-width="150" sortable>
      </el-table-column>
      <!--<el-table-column prop="tradeMsg" label="成交信息" min-width="150" sortable>
      </el-table-column>-->
      <el-table-column label="操作" width="150">
        <template scope="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)" icon="el-icon-edit-outline">编辑
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!--工具条-->
    <el-col :span="24" class="toolbar">
      <el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="pageSize"
                     :total="total"
                     style="float:right;">
      </el-pagination>
    </el-col>

    <!--编辑界面-->
    <el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false">
      <el-form :model="editForm" label-width="80px" :rules="editFormRules" ref="editForm" label-position="left">
        <el-form-item label="编    号">
          <el-input-number v-model="editForm.tradeNo" auto-complete="off" :disabled="true"></el-input-number>
        </el-form-item>
        <el-form-item label="状    态">
          <el-select v-model="editForm.status" placeholder="状态">
            <el-option value="UnTraded" label="未成交"></el-option>
            <el-option value="Traded" label="已成交"></el-option>
            <el-option value="Refused" label="已拒绝"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="成交价">
          <el-input-number v-model="editForm.tradePrice" :min="0" :max="200"></el-input-number>
        </el-form-item>
        <el-form-item label="成交金额">
          <el-input-number v-model="editForm.tradeAmount" auto-complete="off"></el-input-number>
        </el-form-item>
        <el-form-item label="成交时间">

          <el-date-picker v-model="editForm.tradeDate" type="date" placeholder="选择日期" value-format="yyyy-MM-dd"/>
          <el-time-picker v-model="editForm.tradeTime" placeholder="选择时间" value-format="HH:mm:ss"/>
        </el-form-item>
        <el-form-item label="成交信息">
          <el-input v-model="editForm.tradeMsg" auto-complete="off"></el-input>
        </el-form-item>


      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="editFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
      </div>
    </el-dialog>


  </section>
</template>

<script>
  import util from '../utils/util'
  import {editTrade, getTradeListPage} from '../api/api';
  import io from 'socket.io-client';
  var vm

  export default {
    name: "trade-hist",
    data() {
      return {
        socketId:'',
        filters: {
        },
        trades: [],
        total: 12,
        page: 1,
        pageSize: 10,
        listLoading: false,
        sels: [],//列表选中列

        editFormVisible: false,//编辑界面是否显示
        editLoading: false,
        editFormRules: {
          name: [
            {required: true, message: '请输入姓名', trigger: 'blur'}
          ]
        },
        //编辑界面数据
        editForm: {
          tradeNo: 0,
          status: '',
          tradePrice: 0,
          tradeAmount: 0,
          tradeDate: '',
          tradeTime: '',
          tradeMsg: ''

        },


      }
    },
    methods: {
      query() {

      },
      //性别显示转换
      formatSex: function (row, column) {
        return row.sex == 1 ? '男' : row.sex == 0 ? '女' : '未知';
      },
      handleCurrentChange(val) {
        this.page = val;
        this.getTrades();
      },
      //获取用户列表

      getTrades() {
        let para = {
          page: this.page,
          pageSize: this.pageSize,
          filters: this.filters,
        };
        this.listLoading = true;
        getTradeListPage(para).then((res) => {
          this.total = res.data.total;
          this.trades = res.data.trades;
          this.listLoading = false;


          //NProgress.done();
        });
      },

      //显示编辑界面
      handleEdit: function (index, row) {
        this.editFormVisible = true;
        //this.editForm = Object.assign({}, row);
        /*for(var name in this.editForm){
          this.editForm[name]=row[name]
        }*/
        this.editForm['tradeNo'] = row['tradeNo']
        this.editForm['status'] = row['status']
        this.editForm['no'] = row['no']
        this.editForm['tradePrice'] = row['tradePrice']
        this.editForm['tradeAmount'] = row['tradeAmount']
        this.editForm['tradeMsg'] = row['tradeMsg']
        if (row['tradeTms'] != null) {
          this.editForm['tradeDate'] = row['tradeTms'].split(' ')[0]
          this.editForm['tradeTime'] = row['tradeTms'].split(' ')[1]

        }


      },
      //编辑
      editSubmit: function () {
        this.$refs.editForm.validate((valid) => {
          if (valid) {
            this.$confirm('确认提交吗？', '提示', {}).then(() => {
              this.editLoading = true;
              //NProgress.start();
              let para = Object.assign({}, this.editForm);
              //para.birth = (!para.birth || para.birth == '') ? '' : util.formatDate.format(new Date(para.birth), 'yyyy-MM-dd');

              editTrade(para).then((res) => {
                this.editLoading = false;
                //NProgress.done();
                this.$message({
                  message: '提交成功',
                  type: 'success'
                });
                this.$refs['editForm'].resetFields();
                this.editFormVisible = false;
                this.getTrades();
              });
            });
          }
        });
      },

      selsChange: function (sels) {
        this.sels = sels;
      },


      socketio() {
        var socket = io.connect('http://127.0.0.1:5000/echo');
        var name='aaa'
        var vm=this


        socket.on('connect', function () {
          console.log('ws已连接...')
          console.log(name)

          //socket.emit('my event', {data: 'I\'m connected!'});
        })
        socket.on('disconnect', function () {
          console.log('ws已断开...')
        })
        socket.on('my event', function (message) {
          console.log('接收到数据1...' + message)
        })
        socket.on('trade', (message)=> {
          console.log('接收到新交易...' + message)
          var msg='收到来自'+message['custom']+'的新交易,编号：'+message['tradeNo']

          if (Notification.permission === 'granted') {
            var title = 'optionAdmin新消息'
            var options = options || {
              body: msg,
              icon: ''
            }

            new Notification(title, options);
          }
          vm.getTrades()

        })

        this.over = () => {
          socket.close()
        }
      }


    },


    mounted() {
      this.getTrades();
      this.socketio()

      if (Notification.permission == 'default') {
        Notification.requestPermission()
      }
    },
    beforeDestroy() {
      this.over()
    }


  }
</script>

<style scoped>

</style>
