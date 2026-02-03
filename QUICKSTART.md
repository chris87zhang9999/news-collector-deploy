# 快速使用指南

## 第一步：安装和配置

### 1. 进入项目目录
```bash
cd /Users/zhangrui1/news_collector
```

### 2. 运行自动安装脚本
```bash
./setup.sh
```

或手动安装：
```bash
ept uv venv
ept uv pip install -r requirements.txt
```

### 3. 配置微信推送（必须）

#### 方式1: Server酱（推荐，简单）

1. 访问 https://sct.ftqq.com/
2. 使用微信扫码登录
3. 复制你的SendKey
4. 编辑 `config.py`，找到这一行：
   ```python
   'sendkey': 'YOUR_SERVERCHAN_KEY',
   ```
   替换为你的SendKey：
   ```python
   'sendkey': 'SCT123456xxxxx',  # 你的真实SendKey
   ```

#### 方式2: 企业微信机器人

1. 在企业微信群里添加机器人
2. 复制Webhook URL
3. 编辑 `config.py`：
   ```python
   'work_wechat': {
       'enabled': True,
       'webhook_url': '你的Webhook URL',
   }
   ```

## 第二步：测试系统

```bash
ept uv run python main.py test
```

这会：
- ✅ 测试新闻收集功能
- ✅ 测试排序和筛选
- ✅ 生成测试HTML页面
- ✅ （可选）测试微信推送

测试HTML页面保存在 `data/test_news.html`，用浏览器打开查看。

## 第三步：运行一次看看效果

```bash
ept uv run python main.py run
```

执行完成后：
- 📱 微信会收到新闻推送
- 📄 HTML文件保存在 `data/news_YYYYMMDD.html`
- 📝 日志保存在 `data/news_collector.log`

## 第四步：启动定时任务

### 方法1：使用内置调度器（简单）

```bash
ept uv run python main.py schedule
```

程序会在后台运行，每天20:00自动执行。

### 方法2：使用 nohup 后台运行

```bash
nohup ept uv run python main.py schedule > schedule.log 2>&1 &
```

查看进程：
```bash
ps aux | grep "main.py schedule"
```

停止进程：
```bash
kill <进程ID>
```

### 方法3：使用 crontab（最稳定）

编辑crontab：
```bash
crontab -e
```

添加以下行（每天20:00执行）：
```bash
0 20 * * * cd /Users/zhangrui1/news_collector && /Users/zhangrui1/news_collector/.venv/bin/python main.py run >> /Users/zhangrui1/news_collector/cron.log 2>&1
```

查看crontab：
```bash
crontab -l
```

## 进阶配置

### 自定义新闻源

编辑 `config.py`，添加更多RSS源：

```python
NEWS_SOURCES = {
    'rss_feeds': [
        'https://finance.yahoo.com/rss/',
        'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        # 添加你关注的RSS源
        'https://your-favorite-site.com/rss',
    ]
}
```

### 自定义关键词

根据你的兴趣调整关键词：

```python
KEYWORDS = {
    'us_stock': [
        'S&P 500', 'NASDAQ', 'Federal Reserve',
        # 添加你关注的公司或概念
        'NVIDIA', 'Tesla', 'Apple',
    ],
    'ai_robotics': [
        'AI', 'GPT', 'machine learning',
        # 添加你关注的AI技术
        'Claude', 'Gemini', 'transformer',
    ]
}
```

### 调整推送时间

编辑 `config.py`：

```python
SCHEDULE_CONFIG = {
    'daily_time': '08:00',  # 改为早上8点
    'max_news_count': 15,   # 改为推送15条新闻
}
```

### 启用AI摘要（可选）

1. 安装OpenAI库：
```bash
ept uv pip install openai
```

2. 编辑 `config.py`：
```python
AI_CONFIG = {
    'enabled': True,
    'api_key': 'sk-xxxxx',  # 你的OpenAI API Key
    'model': 'gpt-3.5-turbo',
}
```

## 常见问题

### Q: 收不到微信推送？
A:
1. 检查 `config.py` 中的SendKey是否正确
2. 访问 https://sct.ftqq.com/ 查看推送记录
3. 查看 `data/news_collector.log` 日志

### Q: 收集不到新闻？
A:
1. 检查网络连接
2. 某些RSS源可能需要梯子
3. 查看日志文件了解详细错误

### Q: 如何查看历史新闻？
A:
所有HTML文件都保存在 `data/` 目录，文件名格式为 `news_YYYYMMDD.html`

### Q: 如何停止定时任务？
A:
- 内置调度器：按 `Ctrl+C`
- nohup方式：`kill <进程ID>`
- crontab方式：`crontab -e` 删除对应行

## 示例输出

推送到微信的消息格式：

```
📰 每日新闻精选 (2026-02-03)
今日为您精选了 10 条高质量新闻

---

1. 美联储暗示将维持利率不变
分类: 美股 | 来源: CNBC | 评分: 8.5

美联储主席鲍威尔在最新讲话中表示，考虑到通胀压力缓解...

📖 查看详情

---

2. OpenAI发布最新多模态模型
分类: AI/具身智能 | 来源: TechCrunch | 评分: 9.2

OpenAI宣布推出GPT-5预览版，支持视频理解和生成...

📖 查看详情

---
...
```

## 技术支持

- 查看完整文档：`README.md`
- 查看日志文件：`data/news_collector.log`
- 项目目录：`/Users/zhangrui1/news_collector`
