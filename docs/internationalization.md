# 国际化开发指南

## 概述

VisaStatusMonitor 支持完整的国际化（i18n），目前支持中文（简体）和英文，并且设计为可轻松扩展到其他语言。

## 架构设计

### 前端国际化

前端使用 Vue I18n 实现国际化支持：

- **框架**: Vue I18n v9
- **语言检测**: 自动检测浏览器语言
- **语言持久化**: localStorage 保存用户选择
- **回退机制**: 英文作为默认回退语言

### 后端国际化

后端实现自定义的国际化管理器：

- **翻译加载**: JSON 格式的翻译文件
- **动态切换**: 根据用户偏好返回对应语言
- **API 国际化**: 错误消息和响应的多语言支持
- **通知国际化**: 邮件和 Telegram 通知的多语言模板

## 前端实现

### 1. 配置 Vue I18n

```typescript
// frontend/src/locales/index.ts
import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN.json'
import en from './en.json'

const messages = {
  'zh-CN': zhCN,
  'en': en
}

const i18n = createI18n({
  locale: getSavedLocale() || getBrowserLocale(),
  fallbackLocale: 'en',
  messages,
  legacy: false,
  globalInjection: true
})

export default i18n
```

### 2. 语言文件结构

```json
{
  "common": {
    "save": "保存",
    "cancel": "取消",
    "loading": "加载中..."
  },
  "auth": {
    "login": "登录",
    "register": "注册"
  },
  "dashboard": {
    "title": "仪表板",
    "welcome": "欢迎使用 {appName}"
  }
}
```

### 3. 在组件中使用

```vue
<template>
  <div>
    <h1>{{ $t('dashboard.title') }}</h1>
    <p>{{ $t('dashboard.welcome', { appName: 'VisaStatusMonitor' }) }}</p>
    <el-button @click="changeLanguage">
      {{ $t('common.changeLanguage') }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const changeLanguage = () => {
  locale.value = locale.value === 'zh-CN' ? 'en' : 'zh-CN'
  localStorage.setItem('locale', locale.value)
}
</script>
```

### 4. 日期时间本地化

```typescript
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

// 根据当前语言设置 dayjs 语言
const setDayjsLocale = (lang: string) => {
  const dayjsLocale = lang === 'zh-CN' ? 'zh-cn' : 'en'
  dayjs.locale(dayjsLocale)
}

// 格式化日期
const formatDate = (date: string | Date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}
```

## 后端实现

### 1. 国际化管理器

```python
# backend/app/core/i18n.py
import json
import os
from typing import Dict, Optional

class I18nManager:
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_locale = "en"
        self.supported_locales = ["zh-CN", "en"]
        self.load_translations()
    
    def load_translations(self):
        """加载所有翻译文件"""
        for locale in self.supported_locales:
            file_path = f"app/locales/{locale}.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[locale] = json.load(f)
    
    def get_text(self, key: str, locale: str = None, **kwargs) -> str:
        """获取翻译文本"""
        locale = locale or self.default_locale
        
        # 尝试获取指定语言的翻译
        if locale in self.translations:
            text = self._get_nested_value(self.translations[locale], key)
            if text:
                return text.format(**kwargs) if kwargs else text
        
        # 回退到默认语言
        if locale != self.default_locale:
            text = self._get_nested_value(
                self.translations.get(self.default_locale, {}), key
            )
            if text:
                return text.format(**kwargs) if kwargs else text
        
        return key  # 如果都没找到，返回key本身
    
    def _get_nested_value(self, data: dict, key: str):
        """获取嵌套字典的值"""
        keys = key.split('.')
        value = data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value
```

### 2. API 响应国际化

```python
# backend/app/api/base.py
from fastapi import Depends, Header
from app.core.i18n import I18nManager

def get_user_locale(accept_language: str = Header(None)) -> str:
    """从请求头获取用户语言偏好"""
    if accept_language:
        # 解析 Accept-Language 头
        languages = accept_language.split(',')
        for lang in languages:
            lang_code = lang.split(';')[0].strip()
            if lang_code in ['zh-CN', 'zh', 'en']:
                return 'zh-CN' if lang_code.startswith('zh') else 'en'
    return 'en'

def create_response(
    success: bool = True,
    message_key: str = None,
    data: any = None,
    locale: str = Depends(get_user_locale),
    i18n: I18nManager = Depends(get_i18n_manager)
):
    """创建国际化的API响应"""
    message = None
    if message_key:
        message = i18n.get_text(message_key, locale)
    
    return {
        "success": success,
        "message": message,
        "data": data
    }
```

### 3. 通知国际化

```python
# backend/app/services/notification_service.py
class NotificationService:
    def __init__(self, i18n_manager: I18nManager):
        self.i18n = i18n_manager
    
    def send_status_update_email(
        self, 
        user_email: str, 
        user_locale: str,
        applicant_name: str,
        old_status: str,
        new_status: str
    ):
        """发送状态更新邮件"""
        subject = self.i18n.get_text(
            "email.statusUpdate.subject",
            locale=user_locale,
            applicant_name=applicant_name
        )
        
        body = self.i18n.get_text(
            "email.statusUpdate.body",
            locale=user_locale,
            applicant_name=applicant_name,
            old_status=old_status,
            new_status=new_status
        )
        
        # 发送邮件逻辑...
```

## 添加新语言

### 1. 前端添加新语言

1. 创建语言文件：
```bash
cp frontend/src/locales/zh-CN.json frontend/src/locales/fr.json
```

2. 翻译内容：
```json
{
  "common": {
    "save": "Enregistrer",
    "cancel": "Annuler"
  }
}
```

3. 更新配置：
```typescript
// frontend/src/locales/index.ts
import fr from './fr.json'

const messages = {
  'zh-CN': zhCN,
  'en': en,
  'fr': fr
}

const supportedLocales = ['zh-CN', 'en', 'fr']
```

### 2. 后端添加新语言

1. 创建翻译文件：
```bash
cp backend/app/locales/zh-CN.json backend/app/locales/fr.json
```

2. 更新国际化管理器：
```python
class I18nManager:
    def __init__(self):
        self.supported_locales = ["zh-CN", "en", "fr"]
```

## 最佳实践

### 1. 翻译键命名

- 使用点分隔的层级结构：`module.component.text`
- 保持键名的语义化：`auth.login.button` 而不是 `btn1`
- 避免过深的嵌套层级（建议不超过3层）

### 2. 参数化文本

```json
{
  "message": "欢迎 {username}，您有 {count} 条新消息"
}
```

```typescript
$t('message', { username: 'John', count: 5 })
```

### 3. 复数处理

```json
{
  "items": {
    "zero": "没有项目",
    "one": "1个项目", 
    "other": "{count}个项目"
  }
}
```

### 4. 日期时间格式

不同语言使用不同的日期时间格式：

```typescript
const formatters = {
  'zh-CN': 'YYYY年MM月DD日 HH:mm',
  'en': 'MMM DD, YYYY HH:mm'
}
```

### 5. 数字格式

```typescript
const formatNumber = (num: number, locale: string) => {
  return new Intl.NumberFormat(locale).format(num)
}
```

## 测试

### 1. 翻译完整性测试

```typescript
// 检查所有语言文件是否包含相同的键
const checkTranslationKeys = (baseLocale: string, targetLocale: string) => {
  const baseKeys = extractKeys(messages[baseLocale])
  const targetKeys = extractKeys(messages[targetLocale])
  
  const missingKeys = baseKeys.filter(key => !targetKeys.includes(key))
  return missingKeys
}
```

### 2. 语言切换测试

```typescript
// 测试语言切换功能
describe('Language Switching', () => {
  it('should change language when locale is updated', () => {
    const { locale } = useI18n()
    locale.value = 'zh-CN'
    expect(localStorage.getItem('locale')).toBe('zh-CN')
  })
})
```

## 维护

### 1. 翻译文件同步

定期检查翻译文件的同步性，确保所有语言都包含最新的文本键。

### 2. 翻译质量审查

- 定期审查翻译质量
- 收集用户反馈
- 更新过时的翻译

### 3. 自动化工具

考虑使用翻译管理工具：
- 自动检测缺失的翻译
- 翻译文件的版本控制
- 协作翻译平台集成

## 故障排除

### 常见问题

1. **翻译不显示**
   - 检查翻译键是否正确
   - 确认语言文件已正确加载
   - 检查回退机制是否工作

2. **语言切换不生效**
   - 检查 localStorage 是否正确保存
   - 确认组件是否正确响应语言变化

3. **日期格式错误**
   - 检查 dayjs 语言包是否正确加载
   - 确认时区设置是否正确