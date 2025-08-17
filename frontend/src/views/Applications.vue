<template>
  <div class="applications">
    <h1>{{ $t('applications.title') }}</h1>
    <p>{{ $t('applications.subtitle') }}</p>
    
    <div style="margin: 20px 0;">
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        {{ $t('applications.addApplication') }}
      </el-button>
    </div>
    
    <el-table :data="applications" style="width: 100%">
      <el-table-column prop="applicant_name" :label="$t('applications.applicantName')" width="120" />
      <el-table-column prop="country_code" :label="$t('applications.country')" width="80" />
      <el-table-column prop="query_code" :label="$t('applications.queryCode')" width="150" />
      <el-table-column prop="query_type" :label="$t('applications.applicationType')" width="150" />
      <el-table-column prop="status" :label="$t('applications.status')" width="120">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_checked" :label="$t('applications.lastChecked')" width="180" />
      <el-table-column :label="$t('applications.actions')" width="200">
        <template #default="scope">
          <el-button size="small" @click="viewHistory(scope.row)">
            {{ $t('applications.history') }}
          </el-button>
          <el-button size="small" type="primary" @click="editApplication(scope.row)">
            {{ $t('common.edit') }}
          </el-button>
          <el-button size="small" type="danger" @click="deleteApplication(scope.row)">
            {{ $t('common.delete') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 添加申请对话框 -->
    <el-dialog v-model="showAddDialog" :title="$t('applications.addApplication')" width="500px">
      <el-form :model="newApplication" label-width="100px">
        <el-form-item :label="$t('applications.applicantName')">
          <el-input v-model="newApplication.applicant_name" />
        </el-form-item>
        <el-form-item :label="$t('applications.country')">
          <el-select v-model="newApplication.country_code" :placeholder="$t('applications.country')">
            <el-option :label="$t('applications.countryOptions.CZ')" value="CZ" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('applications.queryCode')">
          <el-input v-model="newApplication.query_code" />
        </el-form-item>
        <el-form-item :label="$t('applications.applicationType')">
          <el-select v-model="newApplication.query_type" :placeholder="$t('applications.applicationType')">
            <el-option :label="$t('applications.queryTypes.visa_application_number')" value="visa_application_number" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="addApplication">{{ $t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const showAddDialog = ref(false)
const applications = ref([])

const newApplication = reactive({
  applicant_name: '',
  country_code: '',
  query_code: '',
  query_type: ''
})

const getStatusType = (status: string) => {
  switch (status) {
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    case 'pending': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  if (!status) return t('applications.statusUnknown')
  
  const statusMap: Record<string, string> = {
    'approved': t('applications.statusApproved'),
    'rejected': t('applications.statusRejected'),
    'pending': t('applications.statusPending')
  }
  
  return statusMap[status] || t('applications.statusUnknown')
}

const addApplication = () => {
  // TODO: 实现添加申请逻辑
  showAddDialog.value = false
  ElMessage.success(t('applications.createSuccess'))
}

const editApplication = (app: any) => {
  // TODO: 实现编辑逻辑
  ElMessage.info(t('messages.comingSoon'))
}

const deleteApplication = (app: any) => {
  // TODO: 实现删除逻辑
  ElMessage.info(t('messages.comingSoon'))
}

const viewHistory = (app: any) => {
  // TODO: 实现查看历史逻辑
  ElMessage.info(t('messages.comingSoon'))
}
</script>

<style scoped>
.applications {
  padding: 20px;
}
</style>