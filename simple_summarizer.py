"""
简单摘要增强模块（无需AI）
"""

import re
import logging

logger = logging.getLogger(__name__)


def smart_truncate(text, max_length=300):
    """智能截断文本"""
    if len(text) <= max_length:
        return text

    # 尝试在句子边界截断
    truncated = text[:max_length]

    # 查找最后的句子结束符
    for sep in ['。', '！', '？', '. ', '! ', '? ']:
        last_sep = truncated.rfind(sep)
        if last_sep > max_length * 0.7:
            return truncated[:last_sep + 1]

    return truncated + '...'


def extract_key_info(news):
    """提取关键信息生成中文摘要"""
    title = news.get('title', '')
    summary = news.get('summary', '')
    categories = news.get('categories', [])

    # 合并标题和摘要
    full_text = f"{title}\n\n{summary}"

    # 清理HTML标签
    full_text = re.sub(r'<[^>]+>', '', full_text)

    # 生成简单摘要
    lines = []

    # 添加分类标签
    if categories:
        lines.append(f"【{' | '.join(categories)}】")

    # 添加标题（如果是英文，保留原文）
    lines.append(f"\n{title}")

    # 添加摘要内容
    if summary:
        clean_summary = re.sub(r'\s+', ' ', summary).strip()
        truncated_summary = smart_truncate(clean_summary, 250)
        if truncated_summary:
            lines.append(f"\n{truncated_summary}")

    result = '\n'.join(lines)
    return smart_truncate(result, 300)


def enhance_news_with_summary(news_list):
    """为新闻列表添加增强摘要"""
    for news in news_list:
        if not news.get('ai_summary'):
            news['ai_summary'] = extract_key_info(news)

    return news_list
