#!/bin/bash

echo "======================================"
echo "新闻收集器 - 快速设置"
echo "======================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"
echo ""

# 创建虚拟环境
echo "📦 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
fi
echo ""

# 激活虚拟环境并安装依赖
echo "📦 安装依赖..."
source venv/bin/activate
pip install -r requirements.txt
echo "✅ 依赖安装完成"
echo ""

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data
echo "✅ 数据目录已创建"
echo ""

# 配置提示
echo "⚙️  配置说明"
echo "======================================"
echo ""
echo "1. 微信推送配置（必须）:"
echo "   - 访问 https://sct.ftqq.com/"
echo "   - 使用微信登录"
echo "   - 复制SendKey"
echo "   - 编辑 config.py，将SendKey填入:"
echo "     WECHAT_CONFIG['serverchan']['sendkey'] = 'YOUR_SENDKEY'"
echo ""
echo "2. (可选) NewsAPI配置:"
echo "   - 访问 https://newsapi.org/ 注册"
echo "   - 获取API Key"
echo "   - 编辑 config.py 启用NewsAPI"
echo ""
echo "3. (可选) AI摘要配置:"
echo "   - 获取OpenAI API Key"
echo "   - pip install openai"
echo "   - 编辑 config.py 启用AI_CONFIG"
echo ""
echo "======================================"
echo ""
echo "🚀 快速测试:"
echo "   python main.py test"
echo ""
echo "🚀 启动定时任务:"
echo "   python main.py schedule"
echo ""
echo "📖 详细文档请查看 README.md"
echo ""
