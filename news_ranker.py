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

        # 3. 时效性权重（24小时内统一加分）
        try:
            from dateutil import parser
            if 'published' in news and news['published']:
                pub_date = parser.parse(news['published'])
                hours_old = (datetime.now() - pub_date.replace(tzinfo=None)).total_seconds() / 3600
                # 24小时内的新闻统一加分
                if hours_old < 24:
                    score *= 1.3
                # 超过24小时开始衰减
                elif hours_old < 48:
                    score *= 1.1
        except:
            pass

        # 4. 内容质量评估
        quality_score = self._evaluate_content_quality(news)
        score *= quality_score

        return score

    def _evaluate_content_quality(self, news: Dict) -> float:
        """评估内容质量（1.0-2.0倍）"""
        quality_score = 1.0

        title = news.get('title', '')
        summary = news.get('summary', '')

        # 1. 标题质量评估
        title_quality = self._evaluate_title_quality(title)
        quality_score *= title_quality

        # 2. 摘要质量评估
        summary_quality = self._evaluate_summary_quality(summary)
        quality_score *= summary_quality

        # 3. 信息密度评估（标题+摘要包含的关键信息）
        info_density = self._evaluate_info_density(title, summary)
        quality_score *= info_density

        return min(quality_score, 2.0)  # 最高2倍

    def _evaluate_title_quality(self, title: str) -> float:
        """评估标题质量"""
        if not title:
            return 0.8

        score = 1.0
        title_len = len(title)

        # 长度合适（30-120字符）
        if 30 <= title_len <= 120:
            score *= 1.1
        elif title_len < 15:  # 太短
            score *= 0.9
        elif title_len > 200:  # 太长
            score *= 0.9

        # 检测标题党特征（降低分数）
        clickbait_patterns = [
            r'you won\'t believe',
            r'shocking',
            r'!\s*!\s*!',  # 多个感叹号
            r'click here',
            r'amazing trick',
            r'doctors hate',
        ]

        for pattern in clickbait_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                score *= 0.7
                break

        # 包含数字/数据（通常更有价值）
        if re.search(r'\d+%|\$\d+|\d+年|\d+月|\d+日', title):
            score *= 1.15

        return score

    def _evaluate_summary_quality(self, summary: str) -> float:
        """评估摘要质量"""
        if not summary:
            return 0.9

        score = 1.0
        summary_len = len(summary)

        # 摘要长度评估
        if summary_len < 50:
            score *= 0.9  # 太短，信息量不够
        elif 100 <= summary_len <= 500:
            score *= 1.2  # 长度适中，信息丰富
        elif summary_len > 1000:
            score *= 1.0  # 太长但不减分

        # 句子数量（信息结构）
        sentences = re.split(r'[.!?。！？]', summary)
        sentence_count = len([s for s in sentences if len(s.strip()) > 10])

        if 2 <= sentence_count <= 5:
            score *= 1.1  # 结构良好

        # 包含具体数据/细节
        has_numbers = bool(re.search(r'\d+', summary))
        has_quotes = bool(re.search(r'["\'\u201c\u201d]', summary))  # 检测引号

        if has_numbers:
            score *= 1.1  # 有具体数据
        if has_quotes:
            score *= 1.05  # 有引用

        return score

    def _evaluate_info_density(self, title: str, summary: str) -> float:
        """评估信息密度（包含多少关键概念）"""
        text = (title + ' ' + summary).lower()
        score = 1.0

        # 关键信息类别
        info_categories = {
            '数字数据': [r'\d+%', r'\$\d+', r'\d+\s*(million|billion|trillion)', r'\d+亿', r'\d+万'],
            '时间信息': [r'\d{4}年', r'\d+月', r'today|yesterday|tomorrow|this week', r'今天|昨天|明天'],
            '机构组织': [r'Federal Reserve|SEC|FDA|NASA|Google|Apple|Microsoft|特斯拉|苹果|微软'],
            '专业术语': [r'AI|API|GDP|CPI|IPO|merger|acquisition|算法|模型|芯片'],
            '因果关系': [r'because|due to|as a result|caused by|因为|由于|导致'],
        }

        matched_categories = 0
        for category, patterns in info_categories.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matched_categories += 1
                    break

        # 包含越多类别的信息，质量越高
        if matched_categories >= 4:
            score *= 1.3
        elif matched_categories >= 3:
            score *= 1.2
        elif matched_categories >= 2:
            score *= 1.1
        elif matched_categories == 0:
            score *= 0.95

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
