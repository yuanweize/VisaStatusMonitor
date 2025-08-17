<template>
  <div class="notifications">
    <h1>{{ $t('notifications.title') }}</h1>
    <p>{{ $t('notifications.subtitle') }}</p>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card :header="$t('notifications.settings')">
          <el-form :model="notificationSettings" label-width="120px">
            <el-form-item :label="$t('notifications.globalMethod')">
              <el-select v-model="notificationSettings.global_method" :placeholder="$t('notifications.globalMethod')">
                <el-option :label="$t('notifications.methods.none')" value="none" />
                <el-option :label="$t('notifications.methods.email')" value="email" />
                <el-option :label="$t('notifications.methods.telegram')" value="telegram" />
                <el-option :label="$t('notifications.methods.web')" value="web" />
              </el-select>
            </el-form-item>
            
            <el-form-item :label="$t('notifications.emailAddress')" v-if="notificationSettings.global_method === 'email'">
              <el-input v-model="notificationSettings.email_address" />
            </el-form-item>
            
            <el-form-item :label="$t('notifications.telegramId')" v-if="notificationSettings.global_method === 'telegram'">
              <el-input v-model="notificationSettings.telegram_chat_id" />
            </el-form-item>
            
            <el-form-item :label="$t('notifications.queryInterval')">
              <el-select v-model="notificationSettings.query_interval" :placeholder="$t('notifications.queryInterval')">
                <el-option :label="$t('notifications.intervals.30m')" value="30m" />
                <el-option :label="$t('notifications.intervals.1h')" value="1h" />
                <el-option :label="$t('notifications.intervals.2h')" value="2h" />
                <el-option :label="$t('notifications.intervals.6h')" value="6h" />
                <el-option :label="$t('notifications.intervals.12h')" value="12h" />
                <el-option :label="$t('notifications.intervals.1d')" value="1d" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveSettings">{{ $t('notifications.saveSettings') }}</el-button>
              <el-button @click="testNotification">{{ $t('notifications.testNotification') }}</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card :header="$t('notifications.history')">
          <el-table :data="notificationHistory" style="width: 100%">
            <el-table-column prop="type" :label="$t('notifications.historyColumns.type')" width="80" />
            <el-table-column prop="message" :label="$t('notifications.historyColumns.message')" />
            <el-table-column prop="status" :label="$t('notifications.historyColumns.status')" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'sent' ? 'success' : 'danger'">
                  {{ scope.row.status === 'sent' ? $t('notifications.statusSent') : $t('notifications.statusFailed') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" :label="$t('notifications.historyColumns.time')" width="150" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const notificationSettings = reactive({
  global_method: 'email',
  email_address: '',
  telegram_chat_id: '',
  query_interval: '1h'
})

const notificationHistory = ref([])

const saveSettings = () => {
  // TODO: 实现保存设置逻辑
  ElMessage.success(t('notifications.settingsSaved'))
}

const testNotification = () => {
  // TODO: 实现测试通知逻辑
  ElMessage.success(t('notifications.testSent'))
}
</script>

<style scoped>
.notifications {
  padding: 20px;
}
</style>