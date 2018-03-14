<template>
  <section>

    <!--列表-->
    <el-table :data="datas" highlight-current-row v-loading="listLoading" @selection-change="selsChange"
              style="width: 100%;">
      <el-table-column type="selection" width="55">
      </el-table-column>
      <el-table-column prop="name" label="参数名" width="200" sortable>
      </el-table-column>
      <el-table-column prop="value" label="参数值" width="400" sortable>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template scope="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)" icon="el-icon-edit-outline">编辑
          </el-button>
        </template>
      </el-table-column>


    </el-table>


    <el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false">
      <el-form :model="editForm" label-width="80px" :rules="editFormRules" ref="editForm" label-position="left">

        <el-form-item label="参数名">
          <el-input v-model="editForm.name" auto-complete="off" disabled></el-input>
        </el-form-item>
        <el-form-item label="参数值">
          <el-input v-model="editForm.value" auto-complete="off"></el-input>
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
  import {getSettingList, editSetting} from '../api/api';


  export default {
    name: "setting",
    data() {
      return {
        filters: {
          name: ''
        },
        mode: 1,
        datas: [],
        total: 0,
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
          name: '',
          value: '',

        },


      }
    },
    methods: {
      handleCurrentChange(val) {
        this.page = val;
        this.getSettings();
      },
      //获取用户列表

      getSettings() {
        let para = {};
        this.listLoading = true;
        getSettingList(para).then((res) => {

          this.datas = res.data.settings;
          this.listLoading = false;


          //NProgress.done();
        });
      },

      //显示编辑界面
      handleEdit: function (index, row) {
        this.editFormVisible = true;
        this.editForm = Object.assign({}, row);
        /*for(var name in this.editForm){
          this.editForm[name]=row[name]
        }*/


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

              editSetting(para).then((res) => {
                this.editLoading = false;
                //NProgress.done();
                this.$message({
                  message: '提交成功',
                  type: 'success'
                });
                this.$refs['editForm'].resetFields();
                this.editFormVisible = false;
                this.getSettings();
              });
            });
          }
        });
      },


      selsChange: function (sels) {
        this.sels = sels;
      },

    },
    mounted() {
      this.getSettings();
    }

  }
</script>

<style scoped>

</style>
