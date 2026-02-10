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
请用清晰专业的中文总结以下新闻，要求：

【内容要求】
1. 目标字数约{AI_CONFIG.get('max_summary_length', 400)}字（可适当超出以保证完整性）
2. 用通俗易懂但不失专业的语言，像资深分析师给朋友解读
3. 避免过度娱乐化，保持适度的轻松感
4. **重要：必须完整表达，不要因字数限制而突然截断**

【结构要求】
分为三个部分，每部分必须完整：

**【核心内容】**（优先保证这部分完整）
- 用1-2句话概括发生了什么
- 突出关键数据和重要细节
- 如果是美股新闻：说明涨跌原因、涉及金额/百分比、影响范围
- 如果是AI新闻：说明技术突破点、实际应用、技术指标

**【影响分析】**（如果字数受限可适当精简）
- 对相关行业/领域的影响
- 短期和长期可能带来的变化
- 关联到具体的公司、技术或市场

**【应对建议】**（如果字数受限可适当精简）
- 投资者角度：关注点、机会/风险
- 从业者角度：需要关注的趋势、可能的行动方向
- 保持客观，避免断言式判断

标题: {title}
内容: {content}

请按上述结构输出，使用简洁的小标题（如💡核心、📊影响、💭建议）分隔。
如果内容较复杂，可适当增加长度以确保完整性，但尽量控制在500字以内。
"""

            response = self.client.chat.completions.create(
                model=AI_CONFIG.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "你是一个专业的财经和科技分析师，擅长用清晰易懂的语言解读新闻，并提供有价值的洞察和建议。你的分析客观理性，既不过度乐观也不过度悲观。重要：你会完整表达观点，确保每个部分都有完整的结论，不会突然截断。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,  # 增加token限制，确保有足够空间
                temperature=0.6
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
