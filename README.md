# 麦门年鉴 · maimen-memoir

> 一句话：基于麦当劳中国 MCP，把你一年的麦当劳消费数据，变成一张值得截图分享的「麦门年鉴」。

**你的麦门浓度有多高？** maimen-memoir 聚合你的历史订单、积分账户、优惠券、抽奖记录与活动日历，生成一份 Spotify Wrapped 风格的年度（或任意时段）视觉报告：全年吃了多少单、最爱哪款汉堡、深夜下单率、门店足迹、年度麦门称号……每一项都为「截图发朋友圈」而设计。

## 功能特性

- 📊 **数字总览** — 全年订单数、总消费、用券省钱金额
- 🍔 **口味档案** — TOP 5 最爱餐品排行（含套餐组合透视）
- 🕙 **时间画像** — 早餐党 / 午餐党 / 深夜麦门，一眼定性
- 🗓 **麦门大事记** — 年度第一单、最大手笔、最深夜的一单
- 🏆 **年度称号** — 根据消费画像生成专属认证（如「深夜巨无霸信徒」）
- 📤 **单文件 HTML 输出** — 零依赖、可直接截图分享

## 安装

### 1. 申请麦当劳 MCP Token

前往 [麦当劳 MCP 开放平台](https://open.mcd.cn/mcp)，手机号登录后点击「控制台」→「激活」申请 MCP Token。

### 2. 配置 MCP 连接

复制 `mcp-config.example.json` 并将 `$MCD_MCP_TOKEN` 替换为你的真实 Token（切勿提交真实 Token 到任何仓库）。

### 3. 在 WorkBuddy / Claude Code 中使用

将本仓库的 `skills/maimen-memoir/` 安装为 Skill（或直接将 SKILL.md 内容交给你的 AI 助手），然后说：

> 「帮我生成我的麦门年鉴」

## 使用示例

### 方式一：三步管线（脚本直跑）

```bash
# 1. 采集（8 个只读 MCP 工具）
MCD_TOKEN=你的Token python3 scripts/collect.py work/
# 2. 聚合为 stats.json（--mock 可产出演示数据）
python3 scripts/aggregate.py work/ work/stats.json
# 3. 渲染单文件 HTML 年报
python3 scripts/render.py work/stats.json work/yearbook.html
```

### 方式二：一句话生成（Skill）

在 WorkBuddy / Claude Code 中安装 `skills/maimen-memoir/` 后说：

> 「帮我生成我的麦门年鉴」

AI 会自动走完采集 → 聚合 → 渲染三步，并打开成品。

## 目标用户

- 麦当劳高频消费者（麦门信徒）
- 喜欢 Spotify Wrapped / 网易云年度报告式数据总结的人
- 想知道自己的钱都变成了哪个汉堡的人

## 环境变量

| 变量 | 说明 |
|---|---|
| `MCD_MCP_TOKEN` | 麦当劳 MCP Token（在 [open.mcd.cn/mcp](https://open.mcd.cn/mcp) 申请） |

## 免责声明

本项目为麦当劳程序员创意开发大赛参赛作品，非麦当劳官方产品。数据均来自麦当劳中国 MCP Server 的用户授权查询接口，仅在本机渲染，不上传任何数据。
