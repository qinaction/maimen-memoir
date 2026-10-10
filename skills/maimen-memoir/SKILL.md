---
name: maimen-memoir
description: 麦门年鉴——聚合用户麦当劳消费数据（订单、积分、优惠券、抽奖），生成 Spotify Wrapped 风格的单文件 HTML 年度视觉报告。当用户要求"生成麦门年鉴 / 麦门回忆录 / 我的麦当劳年度报告 / maimen memoir"时使用。
---

# 麦门年鉴（maimen-memoir）

把用户在麦当劳中国的消费数据，变成一张值得截图分享的视觉年报。

## 前置条件

- 已配置麦当劳 MCP 连接器（`https://mcp.mcd.cn`，Bearer Token，Token 由用户自己配置，**任何情况下不询问、不存储、不回显 Token**）
- 本 Skill 仓库已就位（`scripts/` 下有三个脚本）

## 执行流程（三步管线）

### 第一步：采集（scripts/collect.py）

```bash
MCD_TOKEN=<由用户的 MCP 配置注入> python3 scripts/collect.py <工作目录>
```

采集 8 个**只读**工具：`now-time-info`、`query-my-account`、`order-list`、`query-my-coupons`、`mall-order-list`、`query-my-prizes`、`campaign-calendar`、`list-nutrition-foods`。

### 第二步：聚合（scripts/aggregate.py）

```bash
python3 scripts/aggregate.py <采集目录> <工作目录>/stats.json
```

输出 `stats.json`，核心 schema：

```json
{
  "mock": false, "empty": false,
  "period": {"label": "2026"},
  "account": {"available": "0", "accumulative": "0", "used": "0", "expiring": "0"},
  "coupons": 2, "prizes": [{"name": "", "time": ""}],
  "totals": {"orders": 86, "spend": 2347.5, "saved": 0,
             "top_item": "巨无霸", "top_item_cnt": 31,
             "top_store": "高新二路餐厅", "top_store_cnt": 27},
  "months": [{"m": "1月", "n": 5}],
  "tops": [{"name": "巨无霸", "cnt": 31}],
  "slots": [{"name": "夜宵时段（21:00–24:00）", "pct": 34}],
  "timeline": [{"when": "2026年1月18日 · 周日 12:42", "what": "第一单：麦辣鸡腿堡套餐"}],
  "title": {"name": "深夜巨无霸信徒", "desc": "...", "lv": 6, "next": "..."}
}
```

若采集数据为空（`empty: true`）或数据明显过少（< 3 单），主动告知用户：
"你的麦当劳账号暂无消费数据，年报会是空白画布。可以用 `--mock` 先看效果，或去麦当劳下一单再回来生成。"

### 第三步：渲染（scripts/render.py）

```bash
python3 scripts/render.py <工作目录>/stats.json <工作目录>/yearbook.html
```

渲染完成后打开 HTML 交付给用户。

## 设计规范（渲染模板已内置，勿随意改动）

- **单文件 HTML**：样式内联，零外部依赖，可直接截图分享
- **配色**：暗底 `#141210` + 麦当劳红 `#DA291C` + 麦门金 `#FFC72C`
- **结构**：封面（称号 Persona）→ 数字总览 → 月度浓度 → 口味 TOP5 → 时间画像 → 大事记 → 年度认证，共 6 个编号版块
- **时间格式**：北京时间人话格式（"2026年1月18日 · 周日 12:42"），禁止 ISO 格式
- **数据真实性**：仅当用户明确要求"先看效果"时才允许 `mock: true`，且页面底部必须带 `DEMO 数据` 水印；真实数据一律不加水印

## 红线

1. **只用只读工具**——禁止调用 `create-order`、`mall-create-order`、`draw-lottery`、`auto-bind-coupons`、`party-order-create` 等任何产生交易/扣减的工具
2. 不在输出中包含 Token、accountId 等敏感信息
3. 页脚固定声明"非麦当劳官方产品"
4. 外链一律 `target="_blank" rel="noopener noreferrer"`
