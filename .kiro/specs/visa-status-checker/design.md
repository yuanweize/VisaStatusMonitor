# 设计文档

## 概述

签证状态查询系统是一个前后端分离的多国家签证/居留申请状态自动查询和通知系统。后端采用FastAPI提供RESTful API，前端使用现代Web技术提供用户界面。系统采用模块化插件架构，支持多用户管理，提供灵活的通知机制和调度系统。

## 架构

### 整体架构

```mermaid
graph TB
    subgraph "前端 Frontend"
        A[Web界面 Web UI] --> B[用户管理 User Management]
        A --> C[配置管理 Config Management]
        A --> D[状态监控 Status Monitor]
        A --> E[通知设置 Notification Settings]
    end
    
    subgraph "后端 Backend API"
        F[FastAPI Server] --> G[用户认证 Auth]
        F --> H[API路由 API Routes]
        F --> I[数据库 Database]
        F --> J[后台服务 Background Service]
    end
    
    subgraph "核心服务 Core Services"
        J --> K[调度器 Scheduler]
        J --> L[查询引擎 Query Engine]
        J --> M[通知系统 Notification System]
        J --> N[日志系统 Logging System]
        
        L --> O[插件管理器 Plugin Manager]
        O --> P[捷克插件 CZ Plugin]
        O --> Q[其他国家插件 Other Plugins]
        
        M --> R[Telegram通知 TG Notifier]
        M --> S[邮件通知 Email Notifier]
        M --> T[Web通知 Web Notifier]
    end
    
    A -.->|HTTP/WebSocket| F
    I --> U[(SQLite/PostgreSQL)]
```

### 目录结构

```
visa-status-checker/
├── README.md
├── LICENSE
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── requirements.txt
│   ├── main.py                  # FastAPI应用入口
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # 认证API
│   │   │   ├── users.py         # 用户管理API
│   │   │   ├── applications.py  # 申请管理API
│   │   │   ├── notifications.py # 通知设置API
│   │   │   └── status.py        # 状态查询API
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # 配置管理
│   │   │   ├── database.py      # 数据库连接
│   │   │   ├── security.py      # 安全相关
│   │   │   └── scheduler.py     # 后台调度器
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # 用户模型
│   │   │   ├── application.py   # 申请模型
│   │   │   ├── notification.py  # 通知模型
│   │   │   └── query_log.py     # 查询日志模型
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── query_engine.py  # 查询引擎
│   │   │   ├── plugin_manager.py # 插件管理器
│   │   │   └── notification_service.py # 通知服务
│   │   ├── plugins/
│   │   │   ├── __init__.py
│   │   │   ├── base_plugin.py   # 插件基类
│   │   │   └── cz_plugin.py     # 捷克插件
│   │   ├── notifications/
│   │   │   ├── __init__.py
│   │   │   ├── base_notifier.py # 通知基类
│   │   │   ├── telegram_notifier.py # Telegram通知
│   │   │   ├── email_notifier.py # 邮件通知
│   │   │   └── web_notifier.py  # Web通知
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py        # 日志工具
│   │       ├── delay_manager.py # 延迟管理
│   │       └── validators.py    # 数据验证
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_plugins.py
│       └── test_services.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Applications.vue
│   │   │   ├── Notifications.vue
│   │   │   └── Settings.vue
│   │   ├── components/
│   │   │   ├── ApplicationCard.vue
│   │   │   ├── StatusBadge.vue
│   │   │   ├── NotificationSettings.vue
│   │   │   └── CountrySelector.vue
│   │   ├── stores/
│   │   │   ├── auth.js
│   │   │   ├── applications.js
│   │   │   └── notifications.js
│   │   └── utils/
│   │       ├── api.js           # API客户端
│   │       ├── websocket.js     # WebSocket连接
│   │       └── helpers.js       # 工具函数
│   └── public/
│       └── favicon.ico
├── logs/                        # 日志目录
└── docs/
    ├── installation.md
    ├── api_reference.md
    ├── user_guide.md
    └── plugin_development.md
```

## 组件和接口

### 1. 后端API设计

#### 认证API
```python
# POST /api/auth/register
{
    "username": "string",
    "email": "string", 
    "password": "string"
}

# POST /api/auth/login
{
    "username": "string",
    "password": "string"
}

# Response
{
    "access_token": "string",
    "token_type": "bearer",
    "user": {
        "id": "int",
        "username": "string",
        "email": "string"
    }
}
```

#### 申请管理API
```python
# GET /api/applications - 获取用户的所有申请
# POST /api/applications - 创建新申请
{
    "country_code": "CZ",
    "applicant_name": "张三",
    "query_code": "PEKI202508140001",
    "query_type": "visa_application_number",
    "notification_method": "email",  # 可选
    "notification_target": "user@example.com",  # 可选
    "query_interval": "2h"  # 可选
}

# PUT /api/applications/{id} - 更新申请
# DELETE /api/applications/{id} - 删除申请
# GET /api/applications/{id}/status - 获取申请状态历史
```

#### 通知设置API
```python
# GET /api/notifications/settings - 获取用户通知设置
# PUT /api/notifications/settings - 更新通知设置
{
    "global_notification_method": "email",
    "telegram_chat_id": "string",
    "email_address": "string",
    "global_query_interval": "1h"
}

# GET /api/notifications/history - 获取通知历史
```

#### 系统状态API
```python
# GET /api/status/countries - 获取支持的国家列表
# GET /api/status/plugins - 获取插件状态
# GET /api/status/system - 获取系统运行状态
```

### 2. 数据库设计

#### 数据库选择
系统支持两种数据库配置：
- **SQLite**：适合单机部署，数据存储在本地文件中，无需额外配置
- **MySQL**：适合生产环境，支持更高的并发和数据量

#### 数据库配置
```python
# 配置示例
DATABASE_URL = "sqlite:///./data/visa_checker.db"  # SQLite
# 或
DATABASE_URL = "mysql+pymysql://user:password@localhost/visa_checker"  # MySQL
```

#### 用户表 (users)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 申请表 (applications)
```sql
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    applicant_name VARCHAR(100) NOT NULL,
    query_code VARCHAR(50) NOT NULL,
    query_type VARCHAR(50) NOT NULL,
    notification_method VARCHAR(20),
    notification_target VARCHAR(255),
    query_interval VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

#### 查询日志表 (query_logs)
```sql
CREATE TABLE query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    status VARCHAR(50),
    details TEXT,
    query_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    error_message TEXT,
    raw_response TEXT,
    FOREIGN KEY (application_id) REFERENCES applications (id)
);
```

#### 通知记录表 (notifications)
```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    notification_type VARCHAR(20) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    sent_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications (id)
);
```

### 3. 前端组件设计

#### 主要页面组件
```javascript
// Dashboard.vue - 仪表板
- 显示所有申请的状态概览
- 最近状态变化
- 系统运行状态

// Applications.vue - 申请管理
- 申请列表
- 添加/编辑/删除申请
- 状态历史查看

// Notifications.vue - 通知管理
- 通知设置
- 通知历史
- 测试通知功能

// Settings.vue - 系统设置
- 用户个人设置
- 全局配置
- 插件管理
```

#### 状态管理 (Pinia)
```javascript
// stores/applications.js
export const useApplicationsStore = defineStore('applications', {
  state: () => ({
    applications: [],
    currentApplication: null,
    statusHistory: []
  }),
  actions: {
    async fetchApplications(),
    async createApplication(data),
    async updateApplication(id, data),
    async deleteApplication(id),
    async fetchStatusHistory(id)
  }
})
```

### 2. 插件系统

#### 基础插件接口
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePlugin(ABC):
    """查询插件基类"""
    
    @abstractmethod
    def get_country_code(self) -> str:
        """返回国家代码"""
        pass
    
    @abstractmethod
    def get_supported_query_types(self) -> List[str]:
        """返回支持的查询类型"""
        pass
    
    @abstractmethod
    def query_status(self, query_code: str, query_type: str) -> Dict[str, Any]:
        """
        查询申请状态
        
        Args:
            query_code: 查询代码
            query_type: 查询类型
            
        Returns:
            {
                'status': 'success|error',
                'data': {
                    'application_status': str,
                    'last_update': str,
                    'details': str,
                    'raw_response': str
                },
                'error': str  # 仅在status为error时存在
            }
        """
        pass
    
    @abstractmethod
    def validate_query_code(self, query_code: str, query_type: str) -> bool:
        """验证查询代码格式"""
        pass
```

#### 捷克插件实现
```python
import requests
from bs4 import BeautifulSoup
from .base_plugin import BasePlugin

class CzechPlugin(BasePlugin):
    """捷克移民局查询插件"""
    
    BASE_URL = "https://ipc.gov.cz/en/status-of-your-application/"
    
    def get_country_code(self) -> str:
        return "CZ"
    
    def get_supported_query_types(self) -> List[str]:
        return ["visa_application_number"]
    
    def query_status(self, query_code: str, query_type: str) -> Dict[str, Any]:
        try:
            # 实现具体的查询逻辑
            response = self._make_request(query_code)
            parsed_data = self._parse_response(response)
            
            return {
                'status': 'success',
                'data': parsed_data
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _make_request(self, query_code: str) -> requests.Response:
        """发送查询请求"""
        # 实现HTTP请求逻辑
        pass
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """解析响应内容"""
        # 实现HTML解析逻辑
        pass
```

### 3. 通知系统

#### 通知接口
```python
from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    """通知基类"""
    
    @abstractmethod
    def send_notification(self, message: str, recipient: str) -> bool:
        """发送通知"""
        pass
    
    @abstractmethod
    def send_status_update(self, applicant_name: str, old_status: str, 
                          new_status: str, recipient: str) -> bool:
        """发送状态更新通知"""
        pass
    
    @abstractmethod
    def send_daily_summary(self, summaries: List[Dict], recipient: str) -> bool:
        """发送每日摘要"""
        pass
```

### 4. 调度系统

#### 调度器设计
```python
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta

class Scheduler:
    """查询调度器"""
    
    def __init__(self, config_manager, query_engine, notification_system):
        self.config_manager = config_manager
        self.query_engine = query_engine
        self.notification_system = notification_system
        self.running = False
        
    async def start(self):
        """启动调度器"""
        self.running = True
        await asyncio.gather(
            self._schedule_queries(),
            self._schedule_daily_summaries()
        )
    
    async def _schedule_queries(self):
        """调度查询任务"""
        while self.running:
            tenants = self.config_manager.get_tenants()
            
            for tenant in tenants:
                # 添加随机延迟
                delay = self._calculate_delay()
                await asyncio.sleep(delay)
                
                # 执行查询
                await self._execute_query(tenant)
            
            # 等待下次调度
            await asyncio.sleep(self._get_next_interval())
    
    def _calculate_delay(self) -> float:
        """计算随机延迟（1分钟内）"""
        import random
        return random.uniform(0, 60)
```

## 数据模型

### Pydantic模型 (用于API)
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

class ApplicationCreate(BaseModel):
    country_code: str
    applicant_name: str
    query_code: str
    query_type: str
    notification_method: Optional[str] = None
    notification_target: Optional[str] = None
    query_interval: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    country_code: str
    applicant_name: str
    query_code: str
    query_type: str
    notification_method: Optional[str]
    notification_target: Optional[str]
    query_interval: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    latest_status: Optional[str] = None
    last_checked: Optional[datetime] = None

class QueryLogResponse(BaseModel):
    id: int
    application_id: int
    status: str
    details: Optional[str]
    query_timestamp: datetime
    response_time_ms: Optional[int]
    error_message: Optional[str]

class NotificationSettings(BaseModel):
    global_notification_method: str
    telegram_chat_id: Optional[str] = None
    email_address: Optional[str] = None
    global_query_interval: str = "1h"
```

### SQLAlchemy模型 (用于数据库)
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    preferred_language = Column(String(10), default="en")  # 用户首选语言
    timezone = Column(String(50), default="UTC")  # 用户时区
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applications = relationship("Application", back_populates="user")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    country_code = Column(String(2), nullable=False)
    applicant_name = Column(String(100), nullable=False)
    query_code = Column(String(50), nullable=False)
    query_type = Column(String(50), nullable=False)
    notification_method = Column(String(20))
    notification_target = Column(String(255))
    query_interval = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="applications")
    query_logs = relationship("QueryLog", back_populates="application")
    notifications = relationship("Notification", back_populates="application")
```

## 错误处理

### 错误分类和处理策略

1. **网络错误**
   - 连接超时：重试3次，指数退避
   - DNS解析失败：记录错误，跳过本次查询
   - HTTP错误：根据状态码决定是否重试

2. **解析错误**
   - HTML结构变化：记录详细错误，通知管理员
   - 数据格式错误：记录原始响应，继续处理其他查询

3. **配置错误**
   - 配置文件格式错误：启动时验证，显示详细错误信息
   - 查询代码格式错误：跳过该租户，记录警告

4. **通知错误**
   - 邮件发送失败：重试机制，最终记录到日志
   - Telegram API错误：检查token有效性，降级到日志通知

## 测试策略

### 单元测试
- 配置管理器测试
- 插件功能测试
- 通知系统测试
- 工具函数测试

### 集成测试
- 端到端查询流程测试
- 多租户配置测试
- 错误处理测试

### 性能测试
- 并发查询性能测试
- 内存使用监控
- 长时间运行稳定性测试

### 模拟测试
- 网站响应模拟
- 网络故障模拟
- 配置变更测试

## 安全考虑

1. **敏感信息保护**
   - 配置文件加密存储
   - 日志中敏感信息脱敏
   - 环境变量支持

2. **网络安全**
   - HTTPS请求验证
   - 请求频率限制
   - User-Agent设置

3. **数据安全**
   - 查询结果本地存储加密
   - 定期清理历史数据
   - 访问权限控制

## 部署和运维

### Docker支持

#### 后端Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端Dockerfile
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./data/visa_checker.db}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=visa_checker
      - MYSQL_USER=${DB_USER}
      - MYSQL_PASSWORD=${DB_PASSWORD}
      - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    command: --default-authentication-plugin=mysql_native_password

volumes:
  mysql_data:
```

### 实时通信

#### WebSocket支持
```python
# backend/app/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_status_update(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

#### 前端WebSocket客户端
```javascript
// frontend/src/utils/websocket.js
class WebSocketClient {
  constructor() {
    this.ws = null;
    this.reconnectInterval = 5000;
  }

  connect() {
    this.ws = new WebSocket('ws://localhost:8000/ws');
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onclose = () => {
      setTimeout(() => this.connect(), this.reconnectInterval);
    };
  }

  handleMessage(data) {
    // 处理状态更新消息
    if (data.type === 'status_update') {
      // 更新应用状态
    }
  }
}
```

### 前端技术栈

#### Vue 3 + Vite + TypeScript
```json
{
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.4.0",
    "element-plus": "^2.3.0",
    "@element-plus/icons-vue": "^2.1.0",
    "echarts": "^5.4.0",
    "dayjs": "^1.11.0",
    "vue-i18n": "^9.8.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.0",
    "vite": "^4.3.0",
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0",
    "@intlify/unplugin-vue-i18n": "^2.0.0"
  }
}
```

#### 响应式设计
- 支持桌面端和移动端
- 使用Element Plus组件库
- 深色/浅色主题切换
- 完整的国际化支持（中文/英文，可扩展）

### 国际化架构

#### 后端国际化支持
```python
# backend/app/core/i18n.py
from typing import Dict, Optional
import json
import os

class I18nManager:
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_locale = "en"
        self.supported_locales = ["zh-CN", "en"]
        self.load_translations()
    
    def load_translations(self):
        """加载翻译文件"""
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
        if locale != self.default_locale and self.default_locale in self.translations:
            text = self._get_nested_value(self.translations[self.default_locale], key)
            if text:
                return text.format(**kwargs) if kwargs else text
        
        # 如果都没找到，返回key本身
        return key
```

#### 前端国际化配置
```javascript
// frontend/src/locales/index.ts
import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN.json'
import en from './en.json'

const messages = {
  'zh-CN': zhCN,
  'en': en
}

// 获取浏览器语言
function getBrowserLocale(): string {
  const browserLang = navigator.language || navigator.languages[0]
  
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
  return localStorage.getItem('locale')
}

// 保存语言设置
function saveLocale(locale: string): void {
  localStorage.setItem('locale', locale)
}

const i18n = createI18n({
  locale: getSavedLocale() || getBrowserLocale(),
  fallbackLocale: 'en',
  messages,
  legacy: false,
  globalInjection: true
})

export { saveLocale }
export default i18n
```

#### 语言文件结构
```json
// frontend/src/locales/zh-CN.json
{
  "common": {
    "save": "保存",
    "cancel": "取消",
    "delete": "删除",
    "edit": "编辑",
    "add": "添加",
    "loading": "加载中...",
    "success": "成功",
    "error": "错误",
    "confirm": "确认"
  },
  "auth": {
    "login": "登录",
    "register": "注册",
    "username": "用户名",
    "password": "密码",
    "email": "邮箱",
    "loginSuccess": "登录成功",
    "loginFailed": "登录失败"
  },
  "dashboard": {
    "title": "仪表板",
    "totalApplications": "总申请数",
    "activeApplications": "活跃申请",
    "statusUpdates": "状态更新",
    "notifications": "通知发送"
  },
  "applications": {
    "title": "申请管理",
    "addApplication": "添加申请",
    "applicantName": "申请人",
    "country": "国家",
    "queryCode": "查询码",
    "applicationType": "申请类型",
    "status": "状态",
    "lastChecked": "最后检查"
  }
}
```

#### 通知国际化
```python
# backend/app/services/notification_service.py
class NotificationService:
    def __init__(self, i18n_manager):
        self.i18n = i18n_manager
    
    def send_status_update_notification(self, user_locale: str, applicant_name: str, 
                                      old_status: str, new_status: str):
        """发送状态更新通知"""
        subject = self.i18n.get_text(
            "notifications.statusUpdate.subject",
            locale=user_locale,
            applicant_name=applicant_name
        )
        
        message = self.i18n.get_text(
            "notifications.statusUpdate.message",
            locale=user_locale,
            applicant_name=applicant_name,
            old_status=old_status,
            new_status=new_status
        )
        
        # 发送通知逻辑...
```

### 监控和告警
- 系统健康检查接口
- 查询成功率监控
- 异常情况告警
- 性能指标收集
- 实时状态推送
- 用户活动统计
- 多语言支持状态监控