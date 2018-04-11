<template>
  <div>

    <el-table :data="customs" highlight-current-row v-loading="listLoading" @selection-change="selsChange"
              style="width: 100%;">
      <el-table-column type="selection" width="55">
      </el-table-column>
      <el-table-column prop="Id" label="客户Id" width="150" sortable>
      </el-table-column>
      <el-table-column prop="Name" label="客户名称" width="200" sortable>
      </el-table-column>
      <el-table-column prop="Type" label="客户类型" width="100" sortable>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template scope="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)" icon="el-icon-edit-outline">编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!--工具条-->
    <el-col :span="24" class="toolbar">
      <el-button circle type="success" size="mini" @click="handleAdd" icon="el-icon-plus"></el-button>
      <el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="pageSize"
                     :total="total"
                     style="float:right;">
      </el-pagination>
    </el-col>


    <el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false">
      <el-form :model="editForm" label-width="80px" :rules="editFormRules" ref="editForm" label-position="left">
        <el-form-item label="客户ID" prop="Id">
          <el-input v-model="editForm.Id" auto-complete="off" :disabled="isEdit"></el-input>
        </el-form-item>
        <el-form-item label="客户名称" prop="Name">
          <el-input v-model="editForm.Name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="客户类型" prop="Type">
          <el-select v-model="editForm.Type" placeholder="类型">
            <el-option value="VIP" label="VIP"></el-option>
            <el-option value="COMMON" label="普通"></el-option>
          </el-select>
        </el-form-item>


      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="editFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<script>
  import {delCustom, editCustom, getCustomListPage} from '../api/api';

  export default {
    name: "qry-custom",
    data() {
      return {
        socketId: '',
        filters: {},
        customs: [],
        total: 12,
        page: 1,
        pageSize: 10,
        listLoading: false,
        sels: [],//列表选中列
        isEdit: true,

        editFormVisible: false,//编辑界面是否显示
        editLoading: false,
        editFormRules: {
          Id: [
            {required: true, message: '请输入客户Id', trigger: 'blur'}
          ],
          Name: [
            {required: true, message: '请输入客户Name', trigger: 'blur'}
          ],
          Type: [
            {required: true, message: '请输入客户Type', trigger: 'blur'}
          ]
        },
        //编辑界面数据
        editForm: {
          Id: '',
          Name: '',
          Type: '',

        },


      }
    },
    methods: {
      selsChange: function (sels) {
        this.sels = sels;
      },
      handleAdd() {
        this.editFormVisible = true;
        this.isEdit = false;

        this.editForm = Object.assign({}, {});
        //debugger
        if (this.$refs['editForm'] != undefined)
          this.$refs['editForm'].resetFields();
      },

      handleEdit: function (index, row) {
        this.editFormVisible = true;
        this.isEdit = true;
        if (this.$refs['editForm'] != undefined)
          this.$refs['editForm'].resetFields();
        this.editForm = Object.assign({}, row);


      },
      editSubmit: function () {
        this.$refs.editForm.validate((valid) => {
          if (valid) {
            this.$confirm('确认提交吗？', '提示', {}).then(() => {
              this.editLoading = true;
              //NProgress.start();
              let para = Object.assign({}, this.editForm);
              //para.birth = (!para.birth || para.birth == '') ? '' : util.formatDate.format(new Date(para.birth), 'yyyy-MM-dd');

              editCustom(para).then((res) => {
                this.editLoading = false;
                //NProgress.done();
                if (res.data['errCode'] == 0) {
                  this.$message({
                    message: '提交成功',
                    type: 'success'
                  });

                }else{
                  this.$message({
                    message: '提交失败:'+res.data['errMsg'],
                    type: 'error'
                  });
                }


                //this.$refs['editForm'].resetFields();
                this.editFormVisible = false;
                this.getDatas();
              });
            });
          }
        });
      },
      handleDel: function (index, row) {
        this.$confirm('确认删除该记录吗?', '提示', {
          type: 'warning'
        }).then(() => {
          this.listLoading = true;
          //NProgress.start();
          let para = {Id: row.Id};
          delCustom(para).then((res) => {
            this.listLoading = false;
            //NProgress.done();
            this.$message({
              message: '删除成功',
              type: 'success'
            });
            this.getDatas();
          });
        }).catch(() => {

        });
      },
      handleCurrentChange(val) {
        this.page = val;
        this.getDatas();
      },
      getDatas() {
        let para = {
          page: this.page,
          pageSize: this.pageSize,
          filters: this.filters,
        };
        this.listLoading = true;
        getCustomListPage(para).then((res) => {
          this.total = res.data.total;
          this.customs = res.data.customs;
          this.listLoading = false;


          //NProgress.done();
        });
      },


    },
    mounted() {
      this.getDatas();
    },
  }
</script>

<style scoped>

</style>
