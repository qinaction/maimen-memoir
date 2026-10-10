#!/usr/bin/env python3
"""
maimen-memoir · 第二步：数据聚合
把 collect.py 采集的 MCP 响应聚合为 stats.json（渲染器的唯一输入）。
用法: python3 aggregate.py <采集目录> <输出stats.json>
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime

# 位置参数（忽略 --flag）：argv = [script, IN_DIR, OUT?]
_ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
IN_DIR = _ARGS[0] if _ARGS else "demo"
OUT = _ARGS[1] if len(_ARGS) > 1 else os.path.join(IN_DIR, "stats.json")

# 时段分桶（24h 制）：早餐 05:00-10:30 / 午餐 11:00-14:00 / 下午茶 14:00-17:00 / 夜宵 21:00-24:00
SLOTS = [
    ("早餐时段（05:00–10:30）", lambda h: 5 <= h < 11),
    ("午餐时段（11:00–14:00）", lambda h: 11 <= h < 14),
    ("下午茶（14:00–17:00）", lambda h: 14 <= h < 17),
    ("夜宵时段（21:00–24:00）", lambda h: 21 <= h < 24),
]


def load(name):
    """读取采集结果；标准响应抽取 Original Response 的 JSON，人性化 markdown 原样返回"""
    path = os.path.join(IN_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    d = json.load(open(path, encoding="utf-8"))
    text = d["result"]["content"][0]["text"]
    if "## Original Response" in text:
        raw = text.split("## Original Response", 1)[1].strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return {"_markdown": text}


# 演示用 stats（对应 demo/index.html 的展示数据）
MOCK_STATS = {
    "generated_at": "", "mock": True, "empty": False,
    "period": {"label": "2026"},
    "account": {"available": "1024", "accumulative": "2360", "used": "1336", "expiring": "0"},
    "coupons": 5, "prizes": [],
    "totals": {"orders": 86, "spend": 2347.5, "saved": 412.8,
               "top_item": "巨无霸", "top_item_cnt": 31,
               "top_store": "高新二路餐厅", "top_store_cnt": 27},
    "months": [{"m": f"{i}月", "n": n} for i, n in
               enumerate([5, 4, 8, 9, 11, 14, 10, 7, 9, 6, 2, 1], 1)],
    "tops": [{"name": n, "cnt": c} for n, c in
             [("巨无霸", 31), ("麦辣鸡腿堡", 24), ("麦乐鸡(10块)", 18), ("中薯条", 16), ("猪柳蛋麦满分", 12)]],
    "slots": [{"name": "夜宵时段（21:00–24:00）", "pct": 34},
              {"name": "午餐时段（11:00–14:00）", "pct": 29},
              {"name": "下午茶（14:00–17:00）", "pct": 21},
              {"name": "早餐时段（05:00–10:30）", "pct": 16}],
    "timeline": [
        {"when": "2026年1月18日 · 周日 12:42", "what": "第一单：麦辣鸡腿堡套餐"},
        {"when": "2026年4月22日 · 周三 22:17", "what": "最深夜的一单：4 个麦乐鸡 + 可乐"},
        {"when": "2026年6月14日 · 周日 18:03", "what": "最大手笔：¥128 家庭桶"},
        {"when": "2026年9月30日 · 周三 08:36", "what": "首次解锁早餐：猪柳蛋麦满分"},
    ],
    "title": {"name": "深夜巨无霸信徒", "lv": 9,
              "desc": "夜宵时段下单率 34%，巨无霸年度消耗 31 个——你是把 i'm lovin' it 刻进生物钟的人。",
              "next": "麦门段位 · 已满级，圣战士认证"},
}


def main():
    global IN_DIR
    # --mock：跳过真实数据，产出演示 stats（渲染页会带 DEMO 水印）
    if "--mock" in sys.argv:
        sys.argv.remove("--mock")
        mock = True
    else:
        mock = False

    if mock:
        json.dump(MOCK_STATS, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"[mock] -> {OUT}")
        return

    account = load("query-my-account") or {}
    orders = (load("order-list") or {}).get("data", {}).get("list", []) or []
    coupons_md = load("query-my-coupons")
    prizes = (load("query-my-prizes") or {}).get("data", {}).get("prizes", []) or []

    # 优惠券张数：从人性化 markdown 里抠
    coupon_cnt = 0
    if coupons_md and "_markdown" in coupons_md:
        m = re.search(r"共\s*(\d+)\s*张", coupons_md["_markdown"])
        coupon_cnt = int(m.group(1)) if m else 0

    acc = account.get("data", {})
    stats = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mock": mock,
        "period": {"label": str(datetime.now().year), "source": "order-list 近期订单"},
        "account": {
            "available": acc.get("availablePoint", "0"),
            "accumulative": acc.get("accumulativePoint", "0"),
            "used": acc.get("usedPoint", "0"),
            "expiring": acc.get("currentMouthExpirePoint", "0"),
        },
        "coupons": coupon_cnt,
        "prizes": [{"name": p.get("name", ""), "time": p.get("recordTime", "")} for p in prizes[:5]],
        "totals": {"orders": 0, "spend": 0.0, "saved": 0.0,
                   "top_item": "", "top_item_cnt": 0, "top_store": "", "top_store_cnt": 0},
        "months": [], "tops": [], "slots": [], "timeline": [],
        "title": {"name": "", "desc": "", "lv": 0, "next": ""},
        "empty": len(orders) == 0,
    }

    if not orders:
        json.dump(stats, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"[empty] 无订单数据 -> {OUT}")
        return

    # ---- 总量 ----
    total_spend = 0.0
    item_cnt, store_cnt, month_cnt = Counter(), Counter(), Counter()
    hour_cnt = {name: 0 for name, _ in SLOTS}
    parsed = []
    for o in orders:
        try:
            t = datetime.strptime(o["createTime"], "%Y-%m-%d %H:%M:%S")
        except (KeyError, ValueError):
            try:
                t = datetime.fromisoformat(o["createTime"])
            except Exception:
                continue
        parsed.append((t, o))
        total_spend += float(o.get("realTotalAmount") or 0)
        month_cnt[t.month] += 1
        if o.get("storeName"):
            store_cnt[o["storeName"]] += 1
        for p in o.get("orderProductList", []):
            if p.get("productName"):
                item_cnt[p["productName"]] += int(p.get("quantity") or 1)
        for name, match in SLOTS:
            if match(t.hour):
                hour_cnt[name] += 1

    parsed.sort(key=lambda x: x[0])
    tops = item_cnt.most_common(5)
    top_item, top_item_cnt = (tops[0] if tops else ("", 0))
    top_store, top_store_cnt = (store_cnt.most_common(1)[0] if store_cnt else ("", 0))
    stats["totals"] = {
        "orders": len(orders), "spend": round(total_spend, 1), "saved": 0.0,
        "top_item": top_item, "top_item_cnt": top_item_cnt,
        "top_store": top_store, "top_store_cnt": top_store_cnt,
    }

    # ---- 月度（1-12 月全量，含 0）----
    stats["months"] = [{"m": f"{i}月", "n": month_cnt.get(i, 0)} for i in range(1, 13)]

    # ---- 榜单 / 时段 ----
    stats["tops"] = [{"name": n, "cnt": c} for n, c in tops]
    total_orders = max(len(orders), 1)
    stats["slots"] = [{"name": name, "pct": round(c / total_orders * 100)}
                      for name, c in hour_cnt.items() if c > 0]

    # ---- 大事记 ----
    def fmt(t):
        return f"{t.year}年{t.month}月{t.day}日 · 周{'一二三四五六日'[t.weekday()]} {t.strftime('%H:%M')}"
    first_t, first_o = parsed[0]
    biggest = max(parsed, key=lambda x: float(x[1].get("realTotalAmount") or 0))
    latest = max(parsed, key=lambda x: (x[0].hour, x[0].minute))
    timeline = [
        {"when": fmt(first_t), "what": f"第一单：{first_o['orderProductList'][0]['productName'] if first_o.get('orderProductList') else '神秘餐品'}", "hl": ""},
        {"when": fmt(biggest[0]), "what": f"最大手笔：¥{biggest[1].get('realTotalAmount')} {biggest[1].get('storeName','')}", "hl": "¥"},
        {"when": fmt(latest[0]), "what": f"最晚的一单：{latest[0].strftime('%H:%M')} 下单", "hl": "深夜"},
        {"when": fmt(parsed[-1][0]), "what": "最近一单：麦门之魂仍在燃烧", "hl": ""},
    ]
    stats["timeline"] = timeline

    # ---- 称号规则引擎 ----
    slot_pct = {s["name"]: s["pct"] for s in stats["slots"]}
    night = slot_pct.get("夜宵时段（21:00–24:00）", 0)
    morning = slot_pct.get("早餐时段（05:00–10:30）", 0)
    if night >= 30:
        persona = f"深夜{top_item[:5]}信徒"
        desc = f"夜宵下单率 {night}%，{top_item} 年度消耗 {top_item_cnt} 份——你是把 i'm lovin' it 刻进生物钟的人。"
    elif morning >= 30:
        persona = "猪柳蛋晨型人"
        desc = f"早餐时段贡献了 {morning}% 的订单，麦满分比你先见到太阳。"
    else:
        persona = "均衡麦门干饭人"
        desc = f"最爱的{top_item}吃了 {top_item_cnt} 份，不追时段只追热爱。"
    lv = min(9, stats["totals"]["orders"] // 10 + 1)
    stats["title"] = {
        "name": persona, "desc": desc, "lv": lv,
        "next": f"麦门段位 · 距离下一级还差 {lv * 10 - stats['totals']['orders']} 单" if lv < 9 else "麦门段位 · 已满级，圣战士认证",
    }

    json.dump(stats, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[ok] {stats['totals']['orders']} 单 -> {OUT}")


if __name__ == "__main__":
    main()
