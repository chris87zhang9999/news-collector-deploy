"""
新闻收集器配置文件
"""

# 新闻源配置
NEWS_SOURCES = {
    # RSS 源
    'rss_feeds': [
        # 美股财经
        'https://finance.yahoo.com/rss/',
        'https://www.cnbc.com/id/100003114/device/rss/rss.html',  # US Market News
        'https://feeds.marketwatch.com/marketwatch/topstories/',

        # AI 新闻
        'https://www.artificialintelligence-news.com/feed/',
        'https://www.technologyreview.com/feed/',
    ],

    # 可选：NewsAPI (需要API key)
    'newsapi': {
        'enabled': False,
        'api_key': 'YOUR_NEWS_API_KEY',  # 从 https://newsapi.org/ 获取
        'sources': ['bloomberg', 'techcrunch', 'wired', 'the-verge']
    }
}

# 关键词配置
KEYWORDS = {
    'us_stock': [
        'S&P 500', 'Dow Jones', 'NASDAQ', 'Federal Reserve', 'interest rate',
        '美股', '标普', '道琼斯', '纳斯达克', '美联储', '利率',
        'stock market', 'market volatility', 'earnings', 'Wall Street'
    ],

    'ai_robotics': [
        'artificial intelligence', 'AI', 'machine learning', 'deep learning',
        'embodied AI', 'robotics', 'humanoid robot', 'autonomous',
        '人工智能', '深度学习', '机器学习', '具身智能', '机器人',
        'GPT', 'LLM', 'transformer', 'neural network'
    ]
}

# 微信推送配置
import os

WECHAT_CONFIG = {
    # 方式1: Server酱 (推荐，简单易用)
    'serverchan': {
        'enabled': True,
        'sendkey': os.environ.get('SERVERCHAN_KEY', 'SCT312763TuQVpQPBUT8ob4bekUdVbCB1s'),  # 从 https://sct.ftqq.com/ 获取
    },

    # 方式2: 企业微信机器人
    'work_wechat': {
        'enabled': False,
        'webhook_url': 'YOUR_WEBHOOK_URL',
    }
}

# 定时任务配置
SCHEDULE_CONFIG = {
    'daily_time': '20:00',  # 每天晚上8点
    'max_news_count': 10,   # 最多推送10条新闻
}

# AI 摘要配置 (可选)
import os

AI_CONFIG = {
    'enabled': True,

    # 选择你的AI服务
    # 方案1: 智谱AI（推荐，国内访问快）
    'base_url': 'https://open.bigmodel.cn/api/paas/v4/',
    'model': 'glm-4-flash',  # 免费模型
    'api_key': os.environ.get('OPENAI_API_KEY', 'YOUR_AI_API_KEY'),

    # 方案2: Deepseek
    # 'base_url': 'https://api.deepseek.com',
    # 'model': 'deepseek-chat',
    # 'api_key': os.environ.get('OPENAI_API_KEY', 'YOUR_AI_API_KEY'),

    # 方案3: OpenAI官方
    # 'base_url': None,  # 使用默认
    # 'model': 'gpt-3.5-turbo',
    # 'api_key': os.environ.get('OPENAI_API_KEY', 'YOUR_AI_API_KEY'),

    'max_summary_length': 300,  # 摘要最大字数
}

# 数据存储
DATA_DIR = './data'
CACHE_FILE = f'{DATA_DIR}/news_cache.json'
LOG_FILE = f'{DATA_DIR}/news_collector.log'
