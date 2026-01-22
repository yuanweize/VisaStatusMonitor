# 安装指南

## 系统要求

- Docker 和 Docker Compose
- 或者：
  - Python 3.11+
  - Node.js 18+
  - MySQL 8.0+ (可选，默认使用SQLite)

## 快速开始

### 使用Docker Compose（推荐）

1. 克隆项目
```bash
git clone https://github.com/yuanweize/VisaStatusMonitor.git
cd VisaStatusMonitor
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 手动安装

#### 后端安装

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp ../.env.example .env
# 编辑 .env 文件
```

5. 启动后端服务
```bash
uvicorn main:app --reload
```

#### 前端安装

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

## 配置说明

### 必需配置

- `SECRET_KEY`: JWT令牌加密密钥
- `DATABASE_URL`: 数据库连接字符串

### 可选配置

- `SMTP_*`: 邮件通知配置
- `TELEGRAM_BOT_TOKEN`: Telegram通知配置
- `CORS_ORIGINS`: 允许的前端域名

### 国际化配置

系统默认支持中文（简体）和英文：

- 前端会自动检测浏览器语言
- 用户可以在设置中切换语言
- 语言偏好会保存在用户配置中
- 通知消息会根据用户语言发送

如需添加其他语言支持，请参考 [国际化开发指南](internationalization.md)。

## 数据库设置

### SQLite（默认）
无需额外配置，数据库文件将自动创建在 `data/` 目录下。

### MySQL
1. 创建数据库
```sql
CREATE DATABASE visa_checker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 更新环境变量
```bash
DATABASE_URL=mysql+pymysql://username:password@localhost/visa_checker
```

## 故障排除

### 常见问题

1. **端口冲突**
   - 修改 docker-compose.yml 中的端口映射
   - 或停止占用端口的其他服务

2. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证连接字符串是否正确

3. **前端无法访问后端**
   - 检查CORS配置
   - 确认后端服务正常运行

### 日志查看

```bash
# Docker方式
docker-compose logs backend
docker-compose logs frontend

# 手动安装方式
# 后端日志在 logs/ 目录下
# 前端日志在浏览器控制台
```