# 化学实验助手 (Chemistry Lab Assistant)

面向化学专业学生的实验辅助 Web 应用：**文献 AI 解析 → 结构化步骤 → 现场数据记录 → Word 报告导出**。数据默认保存在本机 SQLite，适合个人与实验室小组使用。

![Phase](https://img.shields.io/badge/MVP-Phase%201--4-blue)
![Stack](https://img.shields.io/badge/Frontend-React%20%2B%20Tailwind-61dafb)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)

## 功能概览

| 模块 | 功能 |
|------|------|
| 文献导入 | 上传 PDF / DOCX、添加网址；教师讲义优先 |
| AI 解析 | DeepSeek 提取目的、步骤、预期现象、安全注意 |
| 实验进行 | 分步引导、数值/文字/图片记录、语音输入、自动保存 |
| 报告导出 | 一键生成 Word（三线表、宋体排版） |

## 快速开始（Windows）

### 自己开发

双击 **`启动.bat`**，或：

```powershell
# 终端 1 — 后端
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy config.example.yaml config.yaml   # 首次：填入 DeepSeek API Key
python run.py

# 终端 2 — 前端
cd frontend
npm install
npm run dev
```

浏览器打开：**http://localhost:5173**

### 分享给同学（单窗口）

1. 复制 `backend/config.example.yaml` → `backend/config.yaml`，填入 **自己的** [DeepSeek API 密钥](https://platform.deepseek.com/)
2. 双击 **`分享运行.bat`**
3. 打开 **http://127.0.0.1:8000**

详细说明见 [docs/分享给他人.md](docs/分享给他人.md)

## 配置说明

编辑 `backend/config.yaml`：

```yaml
ai:
  api_key: "sk-你的密钥"
  base_url: "https://api.deepseek.com"
  model: "deepseek-chat"
  proxy: ""   # 无法直连时填 http://127.0.0.1:7890
```

局域网共享时将 `server.host` 改为 `"0.0.0.0"`。

## 项目结构

```
chemistry-lab-assistant/
├── frontend/          # React + TypeScript + Tailwind
├── backend/           # FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── api/       # REST 接口
│   │   ├── models/    # 数据模型
│   │   ├── services/  # 文献解析、记录、Word 导出
│   │   └── ai/        # DeepSeek 接入
│   ├── config.example.yaml
│   └── run.py
├── docs/              # 使用与分享文档
├── scripts/           # 开发脚本
├── legacy/            # 旧版 Flask 原型（已弃用）
├── 启动.bat
└── 分享运行.bat
```

## API 文档

后端启动后访问：http://127.0.0.1:8000/docs

## 技术栈

- **前端**：React 19、TypeScript、Tailwind CSS 4、Vite
- **后端**：Python 3.9+、FastAPI、SQLAlchemy、PyMuPDF、python-docx
- **AI**：DeepSeek API（可扩展其他 OpenAI 兼容接口）
- **数据库**：SQLite（`backend/data/`）

## 开发阶段

| Phase | 内容 | 状态 |
|-------|------|------|
| 1 | 项目骨架 | ✅ |
| 2 | 文献导入与 AI 解析 | ✅ |
| 3 | 数据记录与步骤流转 | ✅ |
| 4 | Word 报告导出 | ✅ |
| 5 | 响应式与离线优化 | 计划中 |

## 安全提示

- **切勿**将 `backend/config.yaml` 提交到 Git 或公开分享
- 实验数据位于 `backend/data/`，打包给他人时请排除

## License

MIT — 见 [LICENSE](LICENSE)
