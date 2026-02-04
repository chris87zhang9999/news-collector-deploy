"""
AI摘要生成模块（可选）
"""

import logging
from typing import Dict, List
from config import AI_CONFIG

logger = logging.getLogger(__name__)


class NewsSummarizer:
    """新闻摘要生成器"""

    def __init__(self):
        self.enabled = AI_CONFIG.get('enabled', False)

        if self.enabled:
            try:
                import openai
                api_key = AI_CONFIG.get('api_key')
                base_url = AI_CONFIG.get('base_url')

                if base_url:
                    # 使用自定义base_url（智谱AI、Deepseek等）
                    self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
                else:
                    # 使用OpenAI官方
                    self.client = openai.OpenAI(api_key=api_key)

                logger.info("AI摘要功能已启用")
            except ImportError:
                logger.warning("未安装openai库，AI摘要功能将禁用")
                self.enabled = False
            except Exception as e:
                logger.error(f"初始化AI客户端失败: {e}")
                self.enabled = False

    def summarize_news(self, news: Dict) -> str:
        """为单条新闻生成摘要"""
        if not self.enabled:
            # 如果未启用AI，返回原始摘要或截断标题
            summary = news.get('summary', news.get('title', ''))
            max_len = AI_CONFIG.get('max_summary_length', 200)
            if len(summary) > max_len:
                return summary[:max_len] + '...'
            return summary

        try:
            title = news.get('title', '')
            content = news.get('summary', '')

            prompt = f"""
请用中文总结以下新闻，要求：
1. 简明扼要，不超过{AI_CONFIG.get('max_summary_length', 200)}字
2. 突出重点和关键信息
3. 如果是美股新闻，重点说明市场波动原因
4. 如果是AI新闻，重点说明技术突破或应用

标题: {title}
内容: {content}
"""

            response = self.client.chat.completions.create(
                model=AI_CONFIG.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻摘要助手。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )

            summary = response.choices[0].message.content.strip()
            logger.info(f"为新闻生成了AI摘要: {title[:30]}...")
            return summary

        except Exception as e:
            logger.error(f"生成AI摘要失败: {e}")
            # 降级到简单摘要
            summary = news.get('summary', news.get('title', ''))
            max_len = AI_CONFIG.get('max_summary_length', 200)
            if len(summary) > max_len:
                return summary[:max_len] + '...'
            return summary

    def batch_summarize(self, news_list: List[Dict]) -> List[Dict]:
        """批量生成摘要"""
        logger.info(f"开始为 {len(news_list)} 条新闻生成摘要...")

        for news in news_list:
            news['ai_summary'] = self.summarize_news(news)

        return news_list

    def simple_summarize(self, text: str, max_length: int = 200) -> str:
        """简单截断摘要（不使用AI）"""
        if len(text) <= max_length:
            return text

        # 尝试在句子边界截断
        truncated = text[:max_length]
        last_period = max(
            truncated.rfind('。'),
            truncated.rfind('.'),
            truncated.rfind('！'),
            truncated.rfind('!'),
        )

        if last_period > max_length * 0.7:  # 如果找到的句号位置还比较合理
            return truncated[:last_period + 1]

        return truncated + '...'
