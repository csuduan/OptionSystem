<template>
  <section>
    <el-col :span="24" style="padding-bottom: 0px;">
      <el-form :inline="true" :model="filters">
        <el-form-item>
          <el-radio-group v-model="mode" disabled>
            <el-radio class="radio" :label="1" >实时</el-radio>
            <el-radio class="radio" :label="0">历史</el-radio>
          </el-radio-group>
        </el-form-item>

      </el-form>
    </el-col>

    <!--列表-->
    <el-table :data="datas" highlight-current-row v-loading="listLoading" @selection-change="selsChange"
              style="width: 100%;">
      <el-table-column type="selection" width="55">
      </el-table-column>
      <el-table-column prop="enquiryNo" label="编号" width="80" sortable>
      </el-table-column>

      <el-table-column prop="tradingDay" label="交易日" width="100" sortable>
      </el-table-column>
      <el-table-column prop="tmPeriod" label="时段" width="100" sortable>
      </el-table-column>
      <el-table-column prop="code" label="股票" width="100" sortable>
      </el-table-column>
      <el-table-column prop="period" label="期限" width="80" sortable>
      </el-table-column>
      <el-table-column prop="strikePct" label="行权比例" width="100" sortable>
      </el-table-column>
      <el-table-column prop="cost" label="费用" width="80" sortable>
      </el-table-column>
      <el-table-column prop="tms" label="时间" min-width="150" sortable>
      </el-table-column>


    </el-table>

    <!--工具条-->
    <el-col :span="24" class="toolbar">
      <el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="pageSize" :total="total"
                     style="float:right;">
      </el-pagination>
    </el-col>



  </section>
</template>

<script>
  import util from '../utils/util'
  import {getEnquiryListPage} from '../api/api';


  export default {
    name: "enquiry",
    data() {
      return {
        filters: {
          name: ''
        },
        mode:1,
        datas:[],
        total: 0,
        page: 1,
        pageSize:10,
        listLoading: false,
        sels: [],//列表选中列



      }
    },
    methods: {
      handleCurrentChange(val) {
        this.page = val;
        this.getEnquirys();
      },
      //获取用户列表

      getEnquirys(){
        let para = {
          page: this.page,
          pageSize:this.pageSize,
          mode: this.mode
        };
        this.listLoading = true;
        getEnquiryListPage(para).then((res) => {
          this.total = res.data.total;
          this.datas = res.data.enquirys;
          this.listLoading = false;


          //NProgress.done();
        });
      },



      selsChange: function (sels) {
        this.sels = sels;
      },

    },
    mounted() {
      this.getEnquirys();
    }

  }
</script>

<style scoped>

</style>
