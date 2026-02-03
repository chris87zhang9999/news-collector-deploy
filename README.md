# 📰 新闻收集器

每天自动收集美股市场和人工智能领域的高质量新闻，并推送到微信。

## ✨ 功能特点

- 📡 **多源新闻收集**: 支持RSS源和NewsAPI
- 🎯 **智能过滤**: 根据关键词自动筛选相关新闻
- ⭐ **质量评分**: 基于来源、关键词、时效性等多维度评分
- 📊 **智能排序**: 每天选择最有价值的10条新闻
- 🤖 **AI摘要**: 可选的AI摘要功能，简化长新闻
- 💬 **微信推送**: 支持Server酱和企业微信推送
- 📱 **移动友好**: 生成响应式HTML页面，手机可访问
- ⏰ **定时任务**: 每天晚上8点自动执行

## 🎯 关注领域

1. **美股市场**
   - 市场波动及原因分析
   - 美联储政策动态
   - 重要财报和经济数据

2. **人工智能**
   - AI技术突破
   - 具身智能和机器人
   - 大模型最新进展

## 🚀 快速开始

### 1. 安装依赖

使用EPT工具（推荐）:
```bash
cd news_collector
ept uv venv
ept uv pip install -r requirements.txt
```

或使用标准pip:
```bash
cd news_collector
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置微信推送

编辑 `config.py`，配置Server酱推送:

```python
WECHAT_CONFIG = {
    'serverchan': {
        'enabled': True,
        'sendkey': 'YOUR_SENDKEY',  # 从 https://sct.ftqq.com/ 获取
    }
}
```

**获取Server酱SendKey:**
1. 访问 https://sct.ftqq.com/
2. 使用微信登录
3. 复制SendKey到配置文件

### 3. 测试系统

```bash
python main.py test
```

系统会:
- 收集新闻
- 测试排序功能
- 生成HTML测试页面
- (可选) 测试微信推送

### 4. 启动定时任务

```bash
python main.py schedule
```

程序将在每天晚上8点自动执行，推送新闻到微信。

## 📖 使用命令

```bash
# 测试系统
python main.py test

# 立即执行一次
python main.py run

# 启动定时任务（每天20:00）
python main.py schedule
```

## ⚙️ 配置说明

### 新闻源配置

在 `config.py` 中配置RSS源和NewsAPI:

```python
NEWS_SOURCES = {
    'rss_feeds': [
        'https://finance.yahoo.com/rss/',
        # 添加更多RSS源
    ],
    'newsapi': {
        'enabled': False,  # 设置为True并配置API key
        'api_key': 'YOUR_API_KEY',
    }
}
```

### 关键词配置

自定义关注的关键词:

```python
KEYWORDS = {
    'us_stock': ['S&P 500', 'Federal Reserve', ...],
    'ai_robotics': ['AI', 'robotics', 'GPT', ...],
}
```

### AI摘要（可选）

如需AI摘要功能:

1. 安装OpenAI库:
```bash
ept uv pip install openai
```

2. 配置API key:
```python
AI_CONFIG = {
    'enabled': True,
    'api_key': 'YOUR_OPENAI_API_KEY',
}
```

## 📂 项目结构

```
news_collector/
├── main.py              # 主程序
├── config.py            # 配置文件
├── news_fetcher.py      # 新闻收集模块
├── news_ranker.py       # 新闻排序模块
├── summarizer.py        # AI摘要模块
├── wechat_notifier.py   # 微信推送模块
├── html_generator.py    # HTML生成模块
├── requirements.txt     # 依赖列表
├── README.md           # 使用文档
└── data/               # 数据目录（自动创建）
    ├── news_*.html     # 每日新闻HTML
    ├── news_cache.json # 新闻缓存
    └── news_collector.log  # 日志文件
```

## 🔧 高级配置

### 使用crontab定时执行（Linux/macOS）

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天20:00执行）
0 20 * * * cd /Users/zhangrui1/news_collector && /Users/zhangrui1/news_collector/venv/bin/python main.py run
```

### 企业微信推送

在 `config.py` 中配置企业微信机器人:

```python
WECHAT_CONFIG = {
    'work_wechat': {
        'enabled': True,
        'webhook_url': 'YOUR_WEBHOOK_URL',
    }
}
```

## 📱 查看新闻

推送到微信后:
1. 点击新闻标题查看摘要
2. 点击"查看详情"跳转到原文
3. HTML文件保存在 `data/` 目录，可用浏览器打开

## 🐛 问题排查

### 无法收集新闻
- 检查网络连接
- 查看 `data/news_collector.log` 日志
- 确认RSS源可访问

### 微信推送失败
- 检查SendKey配置是否正确
- 确认Server酱服务正常
- 查看日志中的错误信息

### 定时任务未执行
- 确认程序在后台运行
- 使用 `nohup python main.py schedule &` 后台运行
- 或使用systemd/crontab管理定时任务

## 📝 License

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
