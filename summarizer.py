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
请用生动有趣的中文总结以下新闻，要求：
1. 不超过{AI_CONFIG.get('max_summary_length', 200)}字
2. 用通俗易懂、口语化的表达，像给朋友讲故事一样
3. 可以使用恰当的比喻、类比让内容更生动
4. 突出有趣的细节和关键数据
5. 如果是美股新闻：用大白话解释市场波动原因，说人话，别用太多专业术语
6. 如果是AI新闻：重点说这个技术能干什么、为什么厉害、对普通人有什么影响
7. 开头可以用一句话hook住读者（例如："又涨了！"、"这下厉害了"、"意想不到"等）
8. 适当使用emoji让内容更轻松（但不要过多，1-2个即可）

标题: {title}
内容: {content}
"""

            response = self.client.chat.completions.create(
                model=AI_CONFIG.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "你是一个幽默风趣的新闻解说员，擅长用轻松有趣的方式讲解新闻，让读者既能get到重点又觉得好玩。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
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
