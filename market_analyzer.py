"""
市场分析模块 - 获取和分析每日股市波动
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config import AI_CONFIG

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """市场分析器"""

    def __init__(self):
        self.ai_enabled = AI_CONFIG.get('enabled', False)

        if self.ai_enabled:
            try:
                import openai
                api_key = AI_CONFIG.get('api_key')
                base_url = AI_CONFIG.get('base_url')

                if base_url:
                    self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
                else:
                    self.client = openai.OpenAI(api_key=api_key)

                logger.info("AI市场分析功能已启用")
            except Exception as e:
                logger.error(f"初始化AI客户端失败: {e}")
                self.ai_enabled = False

    def get_market_data(self) -> Dict:
        """获取当日市场数据"""
        try:
            import yfinance as yf
            import time

            # 主要指数
            indices = {
                'S&P 500': '^GSPC',
                'Dow Jones': '^DJI',
                'NASDAQ': '^IXIC',
                'Russell 2000': '^RUT',
                'VIX': '^VIX'  # 恐慌指数
            }

            # 主要板块ETF
            sectors = {
                '科技': 'XLK',
                '金融': 'XLF',
                '医疗': 'XLV',
                '能源': 'XLE',
                '消费': 'XLY',
                '工业': 'XLI',
                '材料': 'XLB',
                '公用事业': 'XLU'
            }

            market_data = {
                'indices': {},
                'sectors': {},
                'top_gainers': [],
                'top_losers': [],
                'date': datetime.now().strftime('%Y-%m-%d')
            }

            # 获取指数数据
            logger.info("获取主要指数数据...")
            for name, symbol in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='2d')

                    if len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2]
                        change_pct = ((current - previous) / previous) * 100

                        market_data['indices'][name] = {
                            'current': round(current, 2),
                            'change_pct': round(change_pct, 2),
                            'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0
                        }
                        logger.info(f"  {name}: {change_pct:+.2f}%")
                    time.sleep(0.5)  # 避免限流
                except Exception as e:
                    logger.warning(f"获取{name}数据失败: {e}")
                    time.sleep(1)  # 失败后等待更久

            # 获取板块数据
            logger.info("获取板块数据...")
            for name, symbol in sectors.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='2d')

                    if len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2]
                        change_pct = ((current - previous) / previous) * 100

                        market_data['sectors'][name] = {
                            'current': round(current, 2),
                            'change_pct': round(change_pct, 2)
                        }
                        logger.info(f"  {name}板块: {change_pct:+.2f}%")
                    time.sleep(0.5)  # 避免限流
                except Exception as e:
                    logger.warning(f"获取{name}板块数据失败: {e}")
                    time.sleep(1)

            # 获取热门股票异动（简化版，使用固定的大公司列表）
            hot_stocks = {
                'Apple': 'AAPL',
                'Microsoft': 'MSFT',
                'Google': 'GOOGL',
                'Amazon': 'AMZN',
                'Tesla': 'TSLA',
                'NVIDIA': 'NVDA',
                'Meta': 'META',
                'Netflix': 'NFLX'
            }

            logger.info("获取热门股票数据...")
            stock_changes = []
            for name, symbol in hot_stocks.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='2d')

                    if len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2]
                        change_pct = ((current - previous) / previous) * 100

                        stock_changes.append({
                            'name': name,
                            'symbol': symbol,
                            'price': round(current, 2),
                            'change_pct': round(change_pct, 2)
                        })
                    time.sleep(0.5)  # 避免限流
                except Exception as e:
                    logger.warning(f"获取{name}数据失败: {e}")
                    time.sleep(1)

            # 如果没有成功获取到任何数据，返回None
            if not market_data['indices'] and not market_data['sectors'] and not stock_changes:
                logger.error("未能获取任何市场数据")
                return None

            # 排序获取涨跌幅最大的
            if stock_changes:
                stock_changes.sort(key=lambda x: x['change_pct'], reverse=True)
                market_data['top_gainers'] = stock_changes[:3]
                market_data['top_losers'] = stock_changes[-3:]

            return market_data

        except ImportError:
            logger.error("未安装yfinance库，无法获取市场数据")
            return None
        except Exception as e:
            logger.error(f"获取市场数据失败: {e}")
            return None

    def generate_market_analysis(self, market_data: Dict) -> Optional[str]:
        """生成市场分析报告"""
        if not market_data:
            return None

        # 如果没有启用AI，返回简单的数据摘要
        if not self.ai_enabled:
            return self._generate_simple_summary(market_data)

        try:
            # 构建数据摘要
            data_summary = self._format_market_data(market_data)

            prompt = f"""
你是一位资深的美股市场分析师，请基于今日市场数据撰写一份专业的市场分析报告。

【今日市场数据】
{data_summary}

【撰写要求】
请按以下结构完整输出分析报告（约500-600字）：

**📊 市场概况**
- 用2-3句话概括今日三大指数的整体表现
- 特别说明VIX恐慌指数的变化（如市场情绪）
- 成交量是否异常

**🔍 板块分析**
- 列出表现最好和最差的3个板块
- 分析板块异动的可能原因（如政策、财报、行业事件）
- 板块轮动趋势判断

**🏢 个股异动**
- 分析涨幅最大的2-3只个股及原因
- 分析跌幅最大的2-3只个股及原因
- 是否有突发事件或财报驱动

**💡 投资建议**
- **短期（1-2周）**：技术面分析，阻力位/支撑位，短线交易策略
- **中长期（1-3月）**：基本面分析，配置建议，风险提示
- 具体的仓位管理建议（如降低/提升股票仓位）

【注意事项】
- 保持客观理性，避免过度乐观或悲观
- 数据解读要准确，逻辑链条清晰
- 建议要具体可操作，不要泛泛而谈
- 必须完整输出所有部分，不要截断

请直接输出分析报告，使用清晰的小标题（如📊、🔍等）分隔。
"""

            response = self.client.chat.completions.create(
                model=AI_CONFIG.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位拥有15年经验的美股市场分析师，曾在高盛和摩根士丹利工作。你擅长解读市场数据，提供清晰、专业、可操作的投资建议。你的分析报告逻辑严密，数据驱动，同时通俗易懂。"
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            analysis = response.choices[0].message.content.strip()
            logger.info("市场分析报告生成成功")
            return analysis

        except Exception as e:
            logger.error(f"生成市场分析失败: {e}")
            return self._generate_simple_summary(market_data)

    def _format_market_data(self, market_data: Dict) -> str:
        """格式化市场数据为文本"""
        lines = []

        # 指数数据
        lines.append("【主要指数】")
        for name, data in market_data.get('indices', {}).items():
            lines.append(f"  {name}: {data['current']} ({data['change_pct']:+.2f}%)")

        # 板块数据
        lines.append("\n【板块表现】")
        sectors = market_data.get('sectors', {})
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1]['change_pct'], reverse=True)
        for name, data in sorted_sectors:
            lines.append(f"  {name}: {data['change_pct']:+.2f}%")

        # 个股异动
        lines.append("\n【个股涨幅榜】")
        for stock in market_data.get('top_gainers', []):
            lines.append(f"  {stock['name']} ({stock['symbol']}): ${stock['price']} ({stock['change_pct']:+.2f}%)")

        lines.append("\n【个股跌幅榜】")
        for stock in market_data.get('top_losers', []):
            lines.append(f"  {stock['name']} ({stock['symbol']}): ${stock['price']} ({stock['change_pct']:+.2f}%)")

        return '\n'.join(lines)

    def _generate_simple_summary(self, market_data: Dict) -> str:
        """生成简单的数据摘要（无AI版本）"""
        lines = []

        lines.append(f"# 📊 {market_data['date']} 美股市场综述\n")

        lines.append("## 主要指数表现\n")
        for name, data in market_data.get('indices', {}).items():
            emoji = "🔴" if data['change_pct'] < 0 else "🟢"
            lines.append(f"{emoji} **{name}**: {data['current']} ({data['change_pct']:+.2f}%)")

        lines.append("\n## 板块表现\n")
        sectors = market_data.get('sectors', {})
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1]['change_pct'], reverse=True)

        lines.append("**领涨板块：**")
        for name, data in sorted_sectors[:3]:
            lines.append(f"- {name}: {data['change_pct']:+.2f}%")

        lines.append("\n**领跌板块：**")
        for name, data in sorted_sectors[-3:]:
            lines.append(f"- {name}: {data['change_pct']:+.2f}%")

        lines.append("\n## 个股异动\n")
        lines.append("**涨幅榜：**")
        for stock in market_data.get('top_gainers', []):
            lines.append(f"- {stock['name']} ({stock['symbol']}): ${stock['price']} ({stock['change_pct']:+.2f}%)")

        lines.append("\n**跌幅榜：**")
        for stock in market_data.get('top_losers', []):
            lines.append(f"- {stock['name']} ({stock['symbol']}): ${stock['price']} ({stock['change_pct']:+.2f}%)")

        lines.append("\n---\n")
        lines.append("💡 提示：完整的市场分析需要启用AI功能，请在config.py中配置AI_CONFIG。")

        return '\n'.join(lines)

    def create_market_news_item(self) -> Optional[Dict]:
        """创建市场分析作为"新闻"条目"""
        logger.info("=" * 60)
        logger.info("开始生成市场分析报告...")
        logger.info("=" * 60)

        # 获取市场数据
        market_data = self.get_market_data()
        if not market_data:
            logger.error("无法获取市场数据")
            return None

        # 生成分析报告
        analysis = self.generate_market_analysis(market_data)
        if not analysis:
            logger.error("无法生成市场分析")
            return None

        # 构造新闻条目格式
        news_item = {
            'title': f'📊 {market_data["date"]} 美股市场全景分析',
            'link': '#market-analysis',  # 占位链接
            'summary': '今日市场整体波动分析、板块异动、个股表现及投资建议',
            'ai_summary': analysis,
            'source': '市场数据分析',
            'categories': ['美股', '市场分析'],
            'published': datetime.now().isoformat(),
            'score': 999.0,  # 最高分，确保排在第一
            'is_market_analysis': True  # 标记为市场分析
        }

        logger.info("✅ 市场分析报告生成完成")
        return news_item
