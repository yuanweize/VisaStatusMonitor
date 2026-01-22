import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN.json'
import en from './en.json'

const messages = {
  'zh-CN': zhCN,
  'en': en
}

// 获取浏览器语言
function getBrowserLocale(): string {
  const browserLang = navigator.language || (navigator as any).languages?.[0] || 'en'
  
  // 支持的语言列表
  const supportedLocales = ['zh-CN', 'en']
  
  // 精确匹配
  if (supportedLocales.includes(browserLang)) {
    return browserLang
  }
  
  // 语言代码匹配（如 zh 匹配 zh-CN）
  const langCode = browserLang.split('-')[0]
  const matchedLocale = supportedLocales.find(locale => 
    locale.startsWith(langCode)
  )
  
  return matchedLocale || 'en'
}

// 从localStorage获取保存的语言设置
function getSavedLocale(): string | null {
  try {
    return localStorage.getItem('locale')
  } catch {
    return null
  }
}

// 保存语言设置
function saveLocale(locale: string): void {
  try {
    localStorage.setItem('locale', locale)
  } catch (error) {
    console.warn('Failed to save locale to localStorage:', error)
  }
}

// 获取初始语言设置
function getInitialLocale(): string {
  return getSavedLocale() || getBrowserLocale()
}

const i18n = createI18n({
  locale: getInitialLocale(),
  fallbackLocale: 'en',
  messages,
  legacy: false,
  globalInjection: true
})

// 监听语言变化，保存到localStorage
i18n.global.locale.value = getInitialLocale()

export { saveLocale, getSavedLocale, getBrowserLocale }
export default i18n