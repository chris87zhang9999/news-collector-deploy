"""
微信推送模块
"""

import requests
import logging
from typing import List, Dict
from config import WECHAT_CONFIG

logger = logging.getLogger(__name__)


class WeChatNotifier:
    """微信推送通知器"""

    def __init__(self):
        self.serverchan_enabled = WECHAT_CONFIG.get('serverchan', {}).get('enabled', False)
        self.work_wechat_enabled = WECHAT_CONFIG.get('work_wechat', {}).get('enabled', False)

    def send_via_serverchan(self, title: str, content: str) -> bool:
        """
        通过Server酱推送消息
        注册地址: https://sct.ftqq.com/
        """
        if not self.serverchan_enabled:
            logger.info("Server酱未启用")
            return False

        sendkey = WECHAT_CONFIG['serverchan'].get('sendkey', '')
        if not sendkey or sendkey == 'YOUR_SERVERCHAN_KEY':
            logger.error("未配置Server酱SendKey")
            return False

        try:
            url = f"https://sctapi.ftqq.com/{sendkey}.send"
            data = {
                'title': title,
                'desp': content
            }

            response = requests.post(url, data=data, timeout=10)
            result = response.json()

            if result.get('code') == 0:
                logger.info("Server酱推送成功")
                return True
            else:
                logger.error(f"Server酱推送失败: {result.get('message')}")
                return False

        except Exception as e:
            logger.error(f"Server酱推送异常: {e}")
            return False

    def send_via_work_wechat(self, content: str) -> bool:
        """
        通过企业微信机器人推送
        """
        if not self.work_wechat_enabled:
            logger.info("企业微信未启用")
            return False

        webhook_url = WECHAT_CONFIG['work_wechat'].get('webhook_url', '')
        if not webhook_url or webhook_url == 'YOUR_WEBHOOK_URL':
            logger.error("未配置企业微信Webhook URL")
            return False

        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }

            response = requests.post(webhook_url, json=data, timeout=10)
            result = response.json()

            if result.get('errcode') == 0:
                logger.info("企业微信推送成功")
                return True
            else:
                logger.error(f"企业微信推送失败: {result.get('errmsg')}")
                return False

        except Exception as e:
            logger.error(f"企业微信推送异常: {e}")
            return False

    def format_news_markdown(self, news_list: List[Dict]) -> str:
        """
        格式化新闻列表为Markdown
        """
        from datetime import datetime

        markdown = f"# 📰 每日新闻精选 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        markdown += f"今日为您精选了 **{len(news_list)}** 条高质量新闻\n\n"
        markdown += "---\n\n"

        for idx, news in enumerate(news_list, 1):
            title = news.get('title', '无标题')
            link = news.get('link', '')
            categories = ' | '.join(news.get('categories', []))
            source = news.get('source', '未知来源')
            score = news.get('score', 0)

            # 使用AI摘要或原始摘要
            summary = news.get('ai_summary') or news.get('summary', '')
            if len(summary) > 300:
                summary = summary[:300] + '...'

            markdown += f"## {idx}. {title}\n\n"
            markdown += f"**分类**: {categories}  \n"
            markdown += f"**来源**: {source} | **评分**: {score:.1f}  \n\n"

            if summary:
                markdown += f"{summary}\n\n"

            markdown += f"[📖 查看详情]({link})\n\n"
            markdown += "---\n\n"

        markdown += "\n\n💡 Tips: 点击链接查看完整新闻内容\n"

        return markdown

    def send_news_notification(self, news_list: List[Dict]) -> bool:
        """发送新闻通知"""
        if not news_list:
            logger.warning("没有新闻需要推送")
            return False

        from datetime import datetime
        title = f"📰 每日新闻精选 {datetime.now().strftime('%Y-%m-%d')}"
        content = self.format_news_markdown(news_list)

        # 尝试通过Server酱推送
        success = False
        if self.serverchan_enabled:
            success = self.send_via_serverchan(title, content)

        # 如果Server酱失败，尝试企业微信
        if not success and self.work_wechat_enabled:
            success = self.send_via_work_wechat(content)

        return success

    def test_connection(self) -> bool:
        """测试推送连接"""
        test_content = "这是一条测试消息，如果你收到了这条消息，说明配置正确！\n\n发送时间: " + \
                      str(__import__('datetime').datetime.now())

        if self.serverchan_enabled:
            return self.send_via_serverchan("新闻收集器测试", test_content)
        elif self.work_wechat_enabled:
            return self.send_via_work_wechat(test_content)
        else:
            logger.error("未配置任何推送方式")
            return False
