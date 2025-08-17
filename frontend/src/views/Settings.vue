<template>
  <div class="settings">
    <h1>{{ $t('settings.title') }}</h1>
    <p>{{ $t('settings.subtitle') }}</p>
    
    <el-tabs v-model="activeTab" style="margin-top: 20px;">
      <el-tab-pane :label="$t('settings.tabs.personal')" name="personal">
        <el-form :model="personalSettings" label-width="120px">
          <el-form-item :label="$t('settings.personal.username')">
            <el-input v-model="personalSettings.username" disabled />
          </el-form-item>
          <el-form-item :label="$t('settings.personal.email')">
            <el-input v-model="personalSettings.email" />
          </el-form-item>
          <el-form-item :label="$t('settings.personal.language')">
            <el-select v-model="personalSettings.language" @change="changeLanguage">
              <el-option :label="$t('settings.languages.zh-CN')" value="zh-CN" />
              <el-option :label="$t('settings.languages.en')" value="en" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('settings.personal.theme')">
            <el-select v-model="personalSettings.theme">
              <el-option :label="$t('settings.themes.light')" value="light" />
              <el-option :label="$t('settings.themes.dark')" value="dark" />
              <el-option :label="$t('settings.themes.auto')" value="auto" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="savePersonalSettings">{{ $t('common.save') }}</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <el-tab-pane :label="$t('settings.tabs.system')" name="system">
        <el-descriptions :title="$t('settings.system.status')" :column="2" border>
          <el-descriptions-item :label="$t('settings.system.version')">1.0.0</el-descriptions-item>
          <el-descriptions-item :label="$t('settings.system.status')">
            <el-tag type="success">{{ $t('settings.system.statusNormal') }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('settings.system.schedulerStatus')">
            <el-tag type="success">{{ $t('settings.system.statusRunning') }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('settings.system.supportedCountries')">1 ({{ $t('applications.countryOptions.CZ') }})</el-descriptions-item>
          <el-descriptions-item :label="$t('settings.system.totalUsers')">0</el-descriptions-item>
          <el-descriptions-item :label="$t('settings.system.totalApplications')">0</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>
      
      <el-tab-pane :label="$t('settings.tabs.plugins')" name="plugins">
        <el-table :data="plugins" style="width: 100%">
          <el-table-column prop="name" :label="$t('settings.plugins.name')" />
          <el-table-column prop="country" :label="$t('settings.plugins.country')" />
          <el-table-column prop="version" :label="$t('settings.plugins.version')" />
          <el-table-column prop="status" :label="$t('settings.plugins.status')">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
                {{ scope.row.status === 'active' ? $t('settings.plugins.statusActive') : $t('settings.plugins.statusInactive') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="$t('settings.plugins.actions')">
            <template #default="scope">
              <el-button size="small" :type="scope.row.status === 'active' ? 'danger' : 'primary'">
                {{ scope.row.status === 'active' ? $t('settings.plugins.disable') : $t('settings.plugins.enable') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { saveLocale } from '@/locales'

const { t, locale } = useI18n()

const activeTab = ref('personal')

const personalSettings = reactive({
  username: 'admin',
  email: '',
  language: locale.value,
  theme: 'light'
})

const plugins = ref([
  {
    name: t('applications.countryOptions.CZ') + ' Plugin',
    country: t('applications.countryOptions.CZ'),
    version: '1.0.0',
    status: 'active'
  }
])

const changeLanguage = (newLocale: string) => {
  locale.value = newLocale
  saveLocale(newLocale)
  ElMessage.success(t('settings.personal.saveSuccess'))
}

const savePersonalSettings = () => {
  // TODO: 实现保存个人设置逻辑
  ElMessage.success(t('settings.personal.saveSuccess'))
}
</script>

<style scoped>
.settings {
  padding: 20px;
}
</style>