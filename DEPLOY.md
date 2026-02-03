# 云端部署指南

## 为什么要部署到云端？

本地部署的问题：
- ❌ 电脑必须24小时开机
- ❌ 电脑睡眠后定时任务不会执行
- ❌ 耗电、噪音、设备损耗

云端部署的优势：
- ✅ 24小时自动运行
- ✅ 不需要自己的电脑开机
- ✅ 稳定可靠
- ✅ 有免费方案

---

## 方案1：GitHub Actions（免费，推荐⭐）

### 优点
- ✅ 完全免费（每月2000分钟额度）
- ✅ 不需要服务器
- ✅ 配置简单
- ✅ 自动定时执行

### 缺点
- ⚠️ SendKey会存储在GitHub（但是加密的）
- ⚠️ 代码需要上传到GitHub

### 部署步骤

#### 1. 创建GitHub仓库

访问 https://github.com/new 创建一个新仓库（可以设为私有）

#### 2. 上传代码到GitHub

```bash
cd /Users/zhangrui1/news_collector

# 初始化git仓库
git init

# 创建.gitignore
cat > .gitignore << 'EOF'
.venv/
__pycache__/
data/
*.pyc
*.log
.DS_Store
EOF

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: News Collector"

# 关联远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/news_collector.git

# 推送
git push -u origin main
```

#### 3. 添加GitHub Secrets

1. 在GitHub仓库页面，点击 **Settings**
2. 左侧菜单点击 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. Name: `SERVERCHAN_KEY`
5. Secret: 粘贴你的Server酱SendKey（`SCT312763TuQVpQPBUT8ob4bekUdVbCB1s`）
6. 点击 **Add secret**

#### 4. 启用GitHub Actions

1. 在仓库页面点击 **Actions** 标签
2. 如果看到提示，点击 **I understand my workflows, go ahead and enable them**

#### 5. 手动测试运行

1. 点击左侧的 **Daily News Collection**
2. 点击右侧的 **Run workflow**
3. 点击绿色的 **Run workflow** 按钮

等待几分钟，你会在微信收到推送！

#### 6. 修改执行时间（可选）

编辑 `.github/workflows/daily-news.yml` 文件中的这一行：

```yaml
- cron: '0 12 * * *'  # UTC时间12:00 = 北京时间20:00
```

常用时间对照：
- 北京时间 08:00 = UTC 00:00 → `'0 0 * * *'`
- 北京时间 12:00 = UTC 04:00 → `'0 4 * * *'`
- 北京时间 20:00 = UTC 12:00 → `'0 12 * * *'`

---

## 方案2：云服务器（阿里云/腾讯云）

### 优点
- ✅ 完全控制
- ✅ 可以运行其他服务
- ✅ 性能稳定

### 缺点
- 💰 需要付费（约￥100/年起）
- 🔧 需要一些Linux知识

### 部署步骤

#### 1. 购买云服务器

- **阿里云**: https://www.aliyun.com/
- **腾讯云**: https://cloud.tencent.com/
- **学生机**: 约￥10/月

推荐配置：
- 1核2G内存
- Ubuntu 22.04 系统
- 按需选择地区

#### 2. 连接服务器

```bash
ssh root@你的服务器IP
```

#### 3. 安装依赖

```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python和Git
apt install python3 python3-pip git -y

# 安装EPT（可选，也可以直接用pip）
curl -fsSL https://gitlab.chehejia.com/-/snippets/408/raw/master/install.sh | bash
source ~/.bashrc
```

#### 4. 部署代码

```bash
# 克隆代码（如果你已上传到GitHub）
git clone https://github.com/你的用户名/news_collector.git
cd news_collector

# 或者直接从本地上传
# 在本地运行: scp -r /Users/zhangrui1/news_collector root@服务器IP:/root/

# 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. 配置定时任务

```bash
crontab -e
```

添加：
```
0 20 * * * cd /root/news_collector && /root/news_collector/venv/bin/python main.py run >> /root/news_collector/cron.log 2>&1
```

#### 6. 测试运行

```bash
python main.py run
```

收到微信推送就说明成功了！

---

## 方案3：Railway（简单，部分免费）

### 优点
- ✅ 配置超级简单
- ✅ 有免费额度
- ✅ 自动部署

### 缺点
- 💰 免费额度有限（每月$5额度）
- 🌐 需要科学上网访问

### 部署步骤

1. 访问 https://railway.app/
2. 用GitHub账号登录
3. 点击 **New Project** → **Deploy from GitHub repo**
4. 选择你的 news_collector 仓库
5. 添加环境变量 `SERVERCHAN_KEY`
6. 部署完成！

---

## 推荐方案

### 如果你想：
- **完全免费** → 选择 **GitHub Actions**（推荐⭐）
- **完全控制** → 选择 **云服务器**
- **最简单** → 选择 **Railway**

---

## GitHub Actions vs 云服务器对比

| 特性 | GitHub Actions | 云服务器 |
|------|----------------|----------|
| 价格 | 免费 | ￥100+/年 |
| 配置难度 | ⭐⭐ | ⭐⭐⭐⭐ |
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 适用场景 | 定时任务 | 长期运行服务 |

---

## 需要我帮你？

我已经帮你创建好了GitHub Actions配置文件（`.github/workflows/daily-news.yml`），你只需要：

1. 创建GitHub账号（如果没有）
2. 创建仓库并上传代码
3. 添加Secret（你的SendKey）
4. 启用Actions

需要我详细指导某个步骤吗？或者你更倾向于哪种部署方式？
