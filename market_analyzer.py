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
                'earnings_calendar': [],  # 财报日历
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

            # 获取财报日历（未来2周内的财报）
            logger.info("获取财报日历...")
            market_data['earnings_calendar'] = self._get_earnings_calendar(hot_stocks)

            return market_data

        except ImportError:
            logger.error("未安装yfinance库，无法获取市场数据")
            return None
        except Exception as e:
            logger.error(f"获取市场数据失败: {e}")
            return None

    def _get_earnings_calendar(self, stocks: Dict) -> List[Dict]:
        """获取未来2周内的财报日历"""
        try:
            import yfinance as yf
            import time
            from datetime import timedelta

            earnings_list = []
            today = datetime.now()
            two_weeks_later = today + timedelta(days=14)

            for name, symbol in stocks.items():
                try:
                    ticker = yf.Ticker(symbol)

                    # 获取公司信息
                    info = ticker.info

                    # 尝试从calendar获取财报日期
                    calendar = ticker.calendar
                    if calendar is not None and 'Earnings Date' in calendar:
                        earnings_date = calendar['Earnings Date']

                        # 如果是DataFrame或Series，取第一个值
                        if hasattr(earnings_date, 'iloc'):
                            earnings_date = earnings_date.iloc[0] if len(earnings_date) > 0 else None

                        # 检查日期是否在未来2周内
                        if earnings_date and earnings_date < two_weeks_later:
                            earnings_list.append({
                                'name': name,
                                'symbol': symbol,
                                'date': earnings_date.strftime('%Y-%m-%d') if hasattr(earnings_date, 'strftime') else str(earnings_date),
                                'market_cap': info.get('marketCap', 0),
                                'forward_pe': info.get('forwardPE', None),
                                'price': info.get('currentPrice', 0),
                                'analyst_target': info.get('targetMeanPrice', None),
                                'recommendation': info.get('recommendationKey', 'hold')
                            })
                            logger.info(f"  {name} 财报日期: {earnings_date}")

                    time.sleep(0.5)  # 避免限流

                except Exception as e:
                    logger.warning(f"获取{name}财报信息失败: {e}")
                    time.sleep(1)

            # 按财报日期排序
            earnings_list.sort(key=lambda x: x['date'])
            return earnings_list

        except Exception as e:
            logger.error(f"获取财报日历失败: {e}")
            return []

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
你是一位资深的美股市场分析师，拥有深刻的宏观经济洞察力和基本面分析能力。请基于今日市场数据撰写一份专业且深入的市场分析报告。

【今日市场数据】
{data_summary}

【撰写要求】
请按以下结构完整输出分析报告（约700-800字）：

**📊 市场概况**
- 用2-3句话概括今日三大指数的整体表现
- 特别说明VIX恐慌指数的变化及其反映的市场情绪
- 成交量是否异常，资金流向特征

**🔍 深度原因分析（重点）**
- **根本驱动因素**：不要只说"财报超预期"或"数据利好"等表面原因
  - 如果是财报驱动，分析：哪些业务线增长？利润率变化？管理层指引？行业竞争格局变化？
  - 如果是宏观数据，分析：对美联储政策的影响？对企业盈利预期的影响？流动性环境变化？
  - 如果是地缘政治，分析：供应链影响？能源价格传导？避险情绪的持续性？
- **市场情绪与预期差**：市场交易的是什么预期？与共识的差异在哪？
- **资金流向逻辑**：为什么资金流入/流出某些板块？背后的配置逻辑是什么？

**🏢 板块与个股异动**
- 列出表现最好和最差的3个板块，深入分析：
  - 板块异动的产业逻辑（不只是政策，而是产业周期、竞争格局、技术迭代等）
  - 是短期情绪还是长期趋势的开始？
- 个股异动分析（涨跌幅最大的2-3只）：
  - 公司基本面发生了什么变化？
  - 估值是否合理？市场定价的逻辑是什么？

**📅 财报季前瞻（如有财报数据）**
- 列出未来2周即将公布财报的重点公司
- 对每家公司进行预判：
  - **业绩预期**：基于最近行业趋势、公司指引、分析师共识，预计业绩如何？
  - **关键看点**：投资者最关注哪些指标？（如云业务增长、AI芯片出货、用户增长、利润率等）
  - **风险与机会**：可能超预期/不及预期的因素是什么？
  - **股价影响**：如果业绩符合预期，股价会如何反应？（考虑当前估值和市场预期）

**💡 投资建议（具体可操作）**
- **短期策略（1-2周）**：
  - 技术面：关键支撑位/阻力位，成交量特征
  - 事件驱动：即将公布的重要数据/财报，如何布局？
  - 仓位管理：建议提升/降低仓位的具体比例和条件
- **中长期策略（1-3月）**：
  - 基本面配置：看好哪些板块？为什么？（基于产业趋势、估值、政策等）
  - 风险对冲：需要关注的风险点，如何配置防御性资产？
  - 具体标的：如果要配置，重点关注哪些公司？为什么？

【分析原则】
1. **追根溯源**：不要停留在表面现象，要层层深入找到根本原因
2. **数据支撑**：结合具体的估值、增长率、利润率等数据说话
3. **逻辑链条**：清晰地展示"因为A→所以B→因此C"的分析逻辑
4. **预期管理**：明确区分"已经反映在股价中的"和"尚未定价的"
5. **客观理性**：避免过度乐观或悲观，承认不确定性
6. **可执行性**：建议要具体，有明确的触发条件和操作方式

请直接输出分析报告，使用清晰的小标题（如📊、🔍等）分隔，确保每个部分都完整、深入、有价值。
"""

            response = self.client.chat.completions.create(
                model=AI_CONFIG.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位拥有20年经验的美股首席策略师，曾在高盛、摩根士丹利、桥水基金担任要职。你不仅精通技术分析和基本面分析，更擅长追溯市场波动的深层逻辑——从宏观经济周期、产业竞争格局、公司战略变化到市场预期管理。你的分析报告以"深度"著称：不满足于表面现象，而是层层剖析，直击本质。你善于用清晰的逻辑链条、具体的数据和可操作的建议帮助投资者做出明智决策。"
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,  # 增加到1500以支持更长的深度分析
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

        # 财报日历
        earnings = market_data.get('earnings_calendar', [])
        if earnings:
            lines.append("\n【未来2周财报日历】")
            for earn in earnings:
                target_info = f", 分析师目标价: ${earn['analyst_target']:.2f}" if earn.get('analyst_target') else ""
                pe_info = f", 预期PE: {earn['forward_pe']:.1f}" if earn.get('forward_pe') else ""
                lines.append(f"  {earn['date']} - {earn['name']} ({earn['symbol']}): 当前价 ${earn['price']:.2f}{target_info}{pe_info}, 评级: {earn.get('recommendation', 'N/A')}")

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
