#!/usr/bin/env python3
"""
新闻收集器主程序
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path

from news_fetcher import NewsCollector
from news_ranker import NewsRanker
from summarizer import NewsSummarizer
from wechat_notifier import WeChatNotifier
from html_generator import HTMLGenerator
from config import DATA_DIR, CACHE_FILE, LOG_FILE, SCHEDULE_CONFIG

# 设置日志
Path(DATA_DIR).mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NewsCollectorApp:
    """新闻收集器应用"""

    def __init__(self):
        self.collector = NewsCollector()
        self.ranker = NewsRanker()
        self.summarizer = NewsSummarizer()
        self.notifier = WeChatNotifier()
        self.html_gen = HTMLGenerator()

    def run_daily_task(self):
        """执行每日新闻收集任务"""
        logger.info("=" * 60)
        logger.info("开始执行每日新闻收集任务")
        logger.info("=" * 60)

        try:
            # 1. 收集新闻
            logger.info("步骤 1/5: 收集新闻...")
            news_list = self.collector.collect_news()

            if not news_list:
                logger.warning("未收集到任何新闻")
                return

            logger.info(f"收集到 {len(news_list)} 条新闻")

            # 2. 排序和筛选
            logger.info("步骤 2/5: 对新闻进行排序和筛选...")
            max_count = SCHEDULE_CONFIG.get('max_news_count', 10)

            # 先排序，获取足够多的新闻
            ranked_news = self.ranker.rank_news(news_list, top_n=max_count * 3)

            # 如果新闻数量不足，记录警告
            if len(ranked_news) < max_count:
                logger.warning(f"收集到的新闻数量({len(ranked_news)})少于目标数量({max_count})")
                top_news = ranked_news
            else:
                # 在排名靠前的新闻中选择多样性，但确保数量达到max_count
                top_news = self.ranker.diversify_selection(ranked_news, top_n=max_count)

                # 如果多样性选择后数量不足，补充高分新闻
                if len(top_news) < max_count:
                    logger.info(f"多样性选择后只有 {len(top_news)} 条，补充剩余新闻")
                    remaining_needed = max_count - len(top_news)
                    selected_links = {news['link'] for news in top_news}
                    for news in ranked_news:
                        if news['link'] not in selected_links:
                            top_news.append(news)
                            if len(top_news) >= max_count:
                                break

                # 最终按分数排序，确保降序
                top_news = sorted(top_news, key=lambda x: x.get('score', 0), reverse=True)[:max_count]

            logger.info(f"最终筛选出 {len(top_news)} 条高质量新闻")

            # 3. 生成摘要
            logger.info("步骤 3/5: 生成新闻摘要...")
            top_news = self.summarizer.batch_summarize(top_news)

            # 4. 生成HTML页面
            logger.info("步骤 4/5: 生成HTML页面...")
            html_file = os.path.join(DATA_DIR, f"news_{datetime.now().strftime('%Y%m%d')}.html")
            self.html_gen.generate_html(top_news, html_file)
            logger.info(f"HTML页面已保存: {html_file}")

            # 5. 推送到微信
            logger.info("步骤 5/5: 推送新闻到微信...")
            success = self.notifier.send_news_notification(top_news)

            if success:
                logger.info("✅ 新闻推送成功!")
            else:
                logger.warning("⚠️ 新闻推送失败")

            # 保存缓存
            self._save_cache(top_news)

            logger.info("=" * 60)
            logger.info("每日新闻收集任务完成")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"执行任务时发生错误: {e}", exc_info=True)

    def _save_cache(self, news_list):
        """保存新闻缓存"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'news_count': len(news_list),
                'news': news_list
            }

            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"新闻缓存已保存: {CACHE_FILE}")

        except Exception as e:
            logger.error(f"保存缓存失败: {e}")

    def test_system(self):
        """测试系统各模块"""
        logger.info("开始测试新闻收集器系统...")

        # 测试新闻收集
        logger.info("\n1. 测试新闻收集...")
        news_list = self.collector.collect_news()
        logger.info(f"✅ 收集到 {len(news_list)} 条新闻")

        if news_list:
            # 测试排序
            logger.info("\n2. 测试新闻排序...")
            top_news = self.ranker.rank_news(news_list, top_n=3)
            logger.info(f"✅ 筛选出 {len(top_news)} 条新闻")

            # 测试HTML生成
            logger.info("\n3. 测试HTML生成...")
            html_file = os.path.join(DATA_DIR, "test_news.html")
            self.html_gen.generate_html(top_news, html_file)
            logger.info(f"✅ HTML测试文件: {html_file}")

            # 显示示例新闻
            logger.info("\n示例新闻:")
            for idx, news in enumerate(top_news[:2], 1):
                logger.info(f"\n{idx}. {news['title']}")
                logger.info(f"   来源: {news['source']}")
                logger.info(f"   评分: {news['score']:.2f}")
                logger.info(f"   链接: {news['link']}")

        # 测试微信推送
        logger.info("\n4. 测试微信推送...")
        if input("是否测试微信推送? (y/n): ").lower() == 'y':
            self.notifier.test_connection()


def main():
    """主函数"""
    import sys

    app = NewsCollectorApp()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'test':
            # 测试模式
            app.test_system()
        elif command == 'run':
            # 立即执行一次
            app.run_daily_task()
        elif command == 'schedule':
            # 定时任务模式
            import schedule
            import time

            schedule_time = SCHEDULE_CONFIG.get('daily_time', '20:00')
            schedule.every().day.at(schedule_time).do(app.run_daily_task)

            logger.info(f"定时任务已设置，每天 {schedule_time} 执行")
            logger.info("按 Ctrl+C 退出")

            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("\n程序已退出")
        else:
            print("未知命令")
            print_usage()
    else:
        print_usage()


def print_usage():
    """打印使用说明"""
    print("""
新闻收集器 - 使用说明

命令:
  python main.py test      - 测试系统各模块
  python main.py run       - 立即执行一次新闻收集
  python main.py schedule  - 启动定时任务（每天20:00执行）

配置文件:
  config.py - 修改新闻源、关键词、微信推送等配置

首次使用:
  1. 安装依赖: pip install -r requirements.txt
  2. 配置 config.py 中的微信推送 SendKey
  3. 运行测试: python main.py test
  4. 启动定时任务: python main.py schedule
""")


if __name__ == "__main__":
    main()
