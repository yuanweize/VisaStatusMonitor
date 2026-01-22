# VisaStatusMonitor

一个国际化的签证和居留申请状态自动查询系统，采用前后端分离架构，支持多用户的Web界面管理和托管查询服务。

## 功能特性

- 🌍 **多国家支持**: 插件化架构，支持扩展到不同国家的移民局查询
- 👥 **多用户管理**: 支持用户注册、登录和个人申请管理
- 📱 **响应式界面**: 现代化Web界面，支持桌面和移动设备
- 🔔 **多种通知方式**: 支持邮件、Telegram、Web实时通知
- ⏰ **智能调度**: 自动定时查询，避免对目标网站造成压力
- 🔌 **插件系统**: 模块化设计，便于添加新国家支持
- 📊 **状态监控**: 实时状态更新和历史记录查看
- 🌐 **多语言支持**: 支持中英文界面，可扩展其他语言
- 🐳 **容器化部署**: 支持Docker一键部署

## 技术栈

### 后端
- **FastAPI**: 现代化的Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite/MySQL**: 数据存储
- **APScheduler**: 任务调度
- **WebSocket**: 实时通信

### 前端
- **Vue 3**: 渐进式JavaScript框架
- **Vite**: 快速构建工具
- **Element Plus**: UI组件库
- **Pinia**: 状态管理
- **TypeScript**: 类型安全

## 快速开始

### 使用Docker Compose（推荐）

```bash
# 克隆项目
git clone https://github.com/yuanweize/VisaStatusMonitor.git
cd VisaStatusMonitor

# 复制环境变量配置
cp .env.example .env

# 启动服务
docker-compose up -d
```

访问 http://localhost 即可使用系统。

### 手动安装

#### 后端设置

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 前端设置

```bash
cd frontend
npm install
npm run dev
```

## 支持的国家

目前支持的国家和地区：

- 🇨🇿 **捷克共和国** (CZ) - 签证申请状态查询

更多国家支持正在开发中...

## 配置说明

### 环境变量

```bash
# 数据库配置
DATABASE_URL=sqlite:///./data/visa_checker.db

# 安全配置
SECRET_KEY=your-secret-key-here

# 邮件配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Telegram配置
TELEGRAM_BOT_TOKEN=your-bot-token
```

## 开发指南

### 添加新国家支持

1. 在 `backend/app/plugins/` 目录下创建新的插件文件
2. 继承 `BasePlugin` 类并实现必要的方法
3. 在插件管理器中注册新插件

详细开发指南请参考 [插件开发文档](docs/plugin_development.md)

### API文档

启动后端服务后，访问 http://localhost:8000/docs 查看自动生成的API文档。

## 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md) 了解详细信息。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果您遇到问题或有建议，请：

1. 查看 [常见问题](docs/faq.md)
2. 提交 [Issue](https://github.com/yuanweize/VisaStatusMonitor/issues)
3. 参与 [讨论](https://github.com/yuanweize/VisaStatusMonitor/discussions)

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新信息。