"""
新闻排序和评分模块
"""

from typing import List, Dict
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class NewsRanker:
    """新闻排序器"""

    def __init__(self):
        # 高质量来源权重
        self.source_weights = {
            'Bloomberg': 1.5,
            'Reuters': 1.5,
            'CNBC': 1.3,
            'Financial Times': 1.5,
            'Wall Street Journal': 1.5,
            'MIT Technology Review': 1.4,
            'Nature': 1.5,
            'Science': 1.5,
            'TechCrunch': 1.2,
            'Wired': 1.2,
            'The Verge': 1.2,  # 新增
            'Ars Technica': 1.3,  # 新增
        }

        # 关键词重要性权重
        self.keyword_weights = {
            # 高重要性
            'Federal Reserve': 2.0,
            'interest rate': 1.8,
            'market crash': 2.0,
            'earnings': 1.5,
            'breakthrough': 1.8,
            'AGI': 2.0,
            'humanoid robot': 1.7,

            # 中等重要性
            'S&P 500': 1.3,
            'NASDAQ': 1.3,
            'AI': 1.2,
            'machine learning': 1.2,
        }

    def calculate_score(self, news: Dict) -> float:
        """计算新闻分数"""
        score = 1.0

        # 1. 来源权重
        source = news.get('source', '')
        for source_name, weight in self.source_weights.items():
            if source_name.lower() in source.lower():
                score *= weight
                break

        # 2. 关键词权重
        text = (news.get('title', '') + ' ' + news.get('summary', '')).lower()
        for keyword, weight in self.keyword_weights.items():
            if keyword.lower() in text:
                score *= weight

        # 3. 时效性权重（越新越好）
        try:
            from dateutil import parser
            if 'published' in news and news['published']:
                pub_date = parser.parse(news['published'])
                hours_old = (datetime.now() - pub_date.replace(tzinfo=None)).total_seconds() / 3600
                # 12小时内的新闻加分
                if hours_old < 12:
                    score *= 1.3
                elif hours_old < 24:
                    score *= 1.1
        except:
            pass

        # 4. 标题长度（合适的标题长度加分）
        title_len = len(news.get('title', ''))
        if 30 <= title_len <= 100:
            score *= 1.1

        # 5. 有摘要的新闻加分
        if news.get('summary') and len(news.get('summary', '')) > 50:
            score *= 1.2

        return score

    def rank_news(self, news_list: List[Dict], top_n: int = 10) -> List[Dict]:
        """对新闻进行排序，返回前N条"""

        # 计算每条新闻的分数
        for news in news_list:
            news['score'] = self.calculate_score(news)

        # 按分数排序
        sorted_news = sorted(news_list, key=lambda x: x['score'], reverse=True)

        logger.info(f"已对 {len(news_list)} 条新闻进行排序")
        if sorted_news:
            logger.info(f"最高分: {sorted_news[0]['score']:.2f}, 最低分: {sorted_news[-1]['score']:.2f}")

        # 返回前N条
        return sorted_news[:top_n]

    def diversify_selection(self, news_list: List[Dict], top_n: int = 10) -> List[Dict]:
        """确保新闻多样性"""
        selected = []
        category_counts = {'美股': 0, 'AI/具身智能': 0}

        # 先按分数排序
        sorted_news = sorted(news_list, key=lambda x: x.get('score', 0), reverse=True)

        for news in sorted_news:
            if len(selected) >= top_n:
                break

            categories = news.get('categories', [])

            # 尽量平衡不同类别
            can_add = True
            for cat in categories:
                if cat in category_counts and category_counts[cat] >= top_n // 2:
                    # 某个类别已经太多了
                    if all(category_counts.get(c, 0) >= top_n // 2 for c in category_counts):
                        # 所有类别都够了
                        can_add = True
                        break
                    else:
                        can_add = False
                        break

            if can_add:
                selected.append(news)
                for cat in categories:
                    if cat in category_counts:
                        category_counts[cat] += 1

        logger.info(f"多样性选择完成，类别分布: {category_counts}")
        return selected
