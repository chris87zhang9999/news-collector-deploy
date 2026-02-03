"""
新闻收集模块
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from config import NEWS_SOURCES, KEYWORDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsCollector:
    """新闻收集器"""

    def __init__(self):
        self.collected_news = []

    def fetch_rss_feeds(self) -> List[Dict]:
        """从RSS源获取新闻"""
        all_news = []

        for feed_url in NEWS_SOURCES['rss_feeds']:
            try:
                logger.info(f"正在获取RSS源: {feed_url}")
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    news_item = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': feed.feed.get('title', feed_url),
                        'timestamp': datetime.now()
                    }
                    all_news.append(news_item)

                logger.info(f"从 {feed_url} 获取了 {len(feed.entries)} 条新闻")

            except Exception as e:
                logger.error(f"获取RSS源失败 {feed_url}: {str(e)}")

        return all_news

    def fetch_newsapi(self) -> List[Dict]:
        """从NewsAPI获取新闻（可选）"""
        if not NEWS_SOURCES['newsapi']['enabled']:
            return []

        all_news = []
        api_key = NEWS_SOURCES['newsapi']['api_key']

        try:
            # 美股新闻
            url = f"https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': api_key,
                'category': 'business',
                'country': 'us',
                'pageSize': 50
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                for article in articles:
                    news_item = {
                        'title': article.get('title', ''),
                        'link': article.get('url', ''),
                        'summary': article.get('description', ''),
                        'published': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'NewsAPI'),
                        'timestamp': datetime.now()
                    }
                    all_news.append(news_item)

            # AI新闻
            params['q'] = 'artificial intelligence OR AI OR robotics'
            params['category'] = 'technology'
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                for article in articles:
                    news_item = {
                        'title': article.get('title', ''),
                        'link': article.get('url', ''),
                        'summary': article.get('description', ''),
                        'published': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'NewsAPI'),
                        'timestamp': datetime.now()
                    }
                    all_news.append(news_item)

            logger.info(f"从NewsAPI获取了 {len(all_news)} 条新闻")

        except Exception as e:
            logger.error(f"NewsAPI请求失败: {str(e)}")

        return all_news

    def filter_by_keywords(self, news_list: List[Dict]) -> List[Dict]:
        """根据关键词过滤新闻"""
        filtered_news = []

        all_keywords = (
            KEYWORDS['us_stock'] +
            KEYWORDS['ai_robotics']
        )

        for news in news_list:
            text = (news['title'] + ' ' + news['summary']).lower()

            # 检查是否包含关键词
            for keyword in all_keywords:
                if keyword.lower() in text:
                    # 标记新闻类型
                    news['categories'] = []
                    if any(kw.lower() in text for kw in KEYWORDS['us_stock']):
                        news['categories'].append('美股')
                    if any(kw.lower() in text for kw in KEYWORDS['ai_robotics']):
                        news['categories'].append('AI/具身智能')

                    filtered_news.append(news)
                    break

        logger.info(f"关键词过滤后保留 {len(filtered_news)} 条新闻")
        return filtered_news

    def filter_by_date(self, news_list: List[Dict], days: int = 1) -> List[Dict]:
        """过滤最近N天的新闻"""
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = []

        for news in news_list:
            try:
                if 'published' in news and news['published']:
                    # 尝试解析发布时间
                    from dateutil import parser
                    pub_date = parser.parse(news['published'])
                    if pub_date.replace(tzinfo=None) >= cutoff_date:
                        filtered.append(news)
                else:
                    # 如果没有发布时间，保留
                    filtered.append(news)
            except:
                # 解析失败，保留
                filtered.append(news)

        return filtered

    def collect_news(self) -> List[Dict]:
        """收集所有新闻"""
        logger.info("开始收集新闻...")

        # 从各个源获取新闻
        rss_news = self.fetch_rss_feeds()
        api_news = self.fetch_newsapi()

        # 合并新闻
        all_news = rss_news + api_news
        logger.info(f"总共获取 {len(all_news)} 条新闻")

        # 去重
        unique_news = self._deduplicate(all_news)
        logger.info(f"去重后保留 {len(unique_news)} 条新闻")

        # 过滤
        filtered_news = self.filter_by_keywords(unique_news)
        filtered_news = self.filter_by_date(filtered_news, days=1)

        self.collected_news = filtered_news
        return filtered_news

    def _deduplicate(self, news_list: List[Dict]) -> List[Dict]:
        """去重"""
        seen_urls = set()
        unique_news = []

        for news in news_list:
            url = news.get('link', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(news)

        return unique_news
