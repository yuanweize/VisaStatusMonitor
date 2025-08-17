<template>
  <div class="dashboard">
    <h1>{{ $t('dashboard.title') }}</h1>
    <p>{{ $t('dashboard.welcome') }}</p>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-number">0</div>
            <div class="stat-label">{{ $t('dashboard.totalApplications') }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-number">0</div>
            <div class="stat-label">{{ $t('dashboard.activeApplications') }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-number">0</div>
            <div class="stat-label">{{ $t('dashboard.statusUpdates') }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-number">0</div>
            <div class="stat-label">{{ $t('dashboard.notifications') }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
// 仪表板组件
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}
</style>