"""
HTML新闻列表生成器
"""

from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """HTML新闻页面生成器"""

    def generate_html(self, news_list: List[Dict], output_file: str = 'news.html') -> str:
        """生成HTML新闻页面"""

        html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日新闻精选 - {date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}

        .news-list {{
            padding: 20px;
        }}

        .news-item {{
            border-bottom: 1px solid #e0e0e0;
            padding: 20px 0;
            transition: background 0.3s;
        }}

        .news-item:last-child {{
            border-bottom: none;
        }}

        .news-item:hover {{
            background: #f8f9fa;
            padding-left: 10px;
            padding-right: 10px;
            margin-left: -10px;
            margin-right: -10px;
            border-radius: 8px;
        }}

        .news-number {{
            display: inline-block;
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            line-height: 32px;
            border-radius: 50%;
            font-weight: bold;
            margin-right: 12px;
        }}

        .news-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            display: inline;
        }}

        .news-meta {{
            color: #7f8c8d;
            font-size: 13px;
            margin-bottom: 12px;
        }}

        .category-tag {{
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 8px;
        }}

        .category-tag.ai {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}

        .news-summary {{
            color: #34495e;
            font-size: 14px;
            margin: 12px 0;
            line-height: 1.8;
        }}

        .news-link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
            transition: color 0.3s;
        }}

        .news-link:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}

        .news-link::after {{
            content: " →";
        }}

        .score-badge {{
            float: right;
            background: #ffd54f;
            color: #f57f17;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
            font-size: 13px;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}

            .header h1 {{
                font-size: 22px;
            }}

            .news-title {{
                font-size: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 每日新闻精选</h1>
            <p>{date} | 为您精选 {count} 条高质量新闻</p>
        </div>

        <div class="news-list">
            {news_items}
        </div>

        <div class="footer">
            <p>💡 由新闻收集器自动生成 | 每日 20:00 更新</p>
            <p>关注：美股市场 | 人工智能 | 具身智能</p>
        </div>
    </div>
</body>
</html>
"""

        news_items_html = ""
        for idx, news in enumerate(news_list, 1):
            title = news.get('title', '无标题')
            link = news.get('link', '#')
            categories = news.get('categories', [])
            source = news.get('source', '未知来源')
            score = news.get('score', 0)
            summary = news.get('ai_summary') or news.get('summary', '')

            # 限制摘要长度
            if len(summary) > 300:
                summary = summary[:300] + '...'

            # 生成分类标签
            category_html = ""
            for cat in categories:
                css_class = "ai" if "AI" in cat or "智能" in cat else ""
                category_html += f'<span class="category-tag {css_class}">{cat}</span>'

            news_item_html = f"""
            <div class="news-item">
                <div>
                    <span class="news-number">{idx}</span>
                    <h2 class="news-title">{title}</h2>
                    <span class="score-badge">⭐ {score:.1f}</span>
                </div>
                <div class="news-meta">
                    {category_html}
                    <span>来源: {source}</span>
                </div>
                <div class="news-summary">{summary}</div>
                <a href="{link}" class="news-link" target="_blank">查看详情</a>
            </div>
            """
            news_items_html += news_item_html

        html_content = html_template.format(
            date=datetime.now().strftime('%Y年%m月%d日'),
            count=len(news_list),
            news_items=news_items_html
        )

        # 保存到文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML文件已生成: {output_file}")
        except Exception as e:
            logger.error(f"保存HTML文件失败: {e}")

        return html_content
