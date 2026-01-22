# 贡献指南

感谢您对 VisaStatusMonitor 项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现了bug或有功能建议：

1. 检查 [Issues](https://github.com/yuanweize/VisaStatusMonitor/issues) 确认问题未被报告
2. 创建新的Issue，包含：
   - 清晰的标题和描述
   - 重现步骤（如果是bug）
   - 期望的行为
   - 实际的行为
   - 环境信息（操作系统、浏览器等）

### 提交代码

1. **Fork项目**
   ```bash
   git clone https://github.com/yuanweize/VisaStatusMonitor.git
   cd VisaStatusMonitor
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **开发和测试**
   - 遵循代码规范
   - 添加必要的测试
   - 确保所有测试通过

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # 或
   git commit -m "fix: resolve issue with..."
   ```

5. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建Pull Request**
   - 提供清晰的标题和描述
   - 引用相关的Issue
   - 等待代码审查

## 开发环境设置

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 运行测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

## 代码规范

### Python代码

- 使用 [Black](https://black.readthedocs.io/) 格式化代码
- 使用 [isort](https://pycqa.github.io/isort/) 排序导入
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 添加类型注解
- 编写文档字符串

```bash
# 格式化代码
black .
isort .
flake8 .
```

### TypeScript/Vue代码

- 使用 [ESLint](https://eslint.org/) 检查代码
- 遵循 [Vue 3 风格指南](https://v3.vuejs.org/style-guide/)
- 使用TypeScript类型注解
- 组件名使用PascalCase

```bash
# 检查代码
npm run lint
```

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(auth): add JWT token authentication
fix(plugin): resolve Czech plugin parsing issue
docs: update installation guide
```

## 添加新国家支持

如果您想添加新国家的签证查询支持：

1. 阅读 [插件开发指南](docs/plugin_development.md)
2. 在 `backend/app/plugins/` 创建新插件
3. 添加相应的测试
4. 更新文档
5. 提交Pull Request

## 翻译

我们欢迎多语言翻译贡献：

### 前端翻译

1. 复制 `frontend/src/locales/zh-CN.json` 为新语言文件
2. 翻译所有文本内容为目标语言
3. 在 `frontend/src/locales/index.ts` 中添加新语言配置
4. 更新支持的语言列表
5. 测试翻译效果和语言切换功能

### 后端翻译

1. 复制 `backend/app/locales/zh-CN.json` 为新语言文件
2. 翻译API响应消息和通知模板
3. 在国际化管理器中注册新语言
4. 测试通知和错误消息的多语言支持

### 翻译质量要求

- 保持术语的一致性
- 考虑目标语言的文化背景
- 确保翻译的准确性和自然性
- 遵循目标语言的格式约定（日期、数字等）

## 文档贡献

文档改进同样重要：

- 修复错别字和语法错误
- 改进说明的清晰度
- 添加示例和截图
- 翻译文档

## 社区准则

### 行为准则

- 尊重所有参与者
- 使用友善和包容的语言
- 接受建设性的批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 沟通渠道

- GitHub Issues: 报告问题和功能请求
- GitHub Discussions: 一般讨论和问答
- Pull Requests: 代码审查和讨论

## 许可证

通过贡献代码，您同意您的贡献将在 [MIT许可证](LICENSE) 下授权。

## 获得帮助

如果您需要帮助：

1. 查看 [文档](docs/)
2. 搜索现有的 [Issues](https://github.com/yuanweize/VisaStatusMonitor/issues)
3. 创建新的Issue或Discussion
4. 联系维护者

感谢您的贡献！🎉