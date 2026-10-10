#!/usr/bin/env python3
"""
maimen-memoir · 第三步：渲染年报
输入 stats.json（aggregate.py 的输出，或手写 mock），输出单文件 HTML。
用法: python3 render.py <stats.json> <输出.html>
"""
import json
import sys

STATS_PATH = sys.argv[1] if len(sys.argv) > 1 else "demo/stats.json"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "demo/yearbook.html"
S = json.load(open(STATS_PATH, encoding="utf-8"))

empty = S.get("empty", False)
mock = S.get("mock", False)
hero_sub = "这一年，你与麦当劳的 365 天，都在这里了" if not empty else "麦门虚位以待，就等你下单开光"


def esc(x):
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


T = S.get("totals", {})
months = S.get("months", [])
peak = max((m["n"] for m in months), default=0)
tops = S.get("tops", [])
max_top = tops[0]["cnt"] if tops else 1
slots = S.get("slots", [])
timeline = S.get("timeline", [])
title = S.get("title", {})

# 空数据兜底：没有订单也能渲染，数字为 0 + 引导文案
months_html = "".join(
    f'<div class="bar {"peak" if m["n"] == peak and peak else ""}">'
    f'<b>{m["n"] or ""}</b><i style="height:{max(round(m["n"] / peak * 100), 4) if peak else 4}%"></i>'
    f'<em>{m["m"]}</em></div>' for m in months)
tops_html = "".join(
    f'<div class="row"><div class="no">{i + 1}</div><div class="name">{esc(t["name"])}</div>'
    f'<div class="bar-bg"><i style="width:{t["cnt"] / max(max_top, 1) * 100:.0f}%"></i></div>'
    f'<div class="cnt">×{t["cnt"]}</div></div>' for i, t in enumerate(tops)) or \
    '<div class="row"><div class="name" style="color:var(--sub)">暂无数据——去麦当劳下一单，年鉴才有的写</div></div>'
slots_html = "".join(
    f'<div class="slot"><div class="top"><b>{esc(s["name"])}</b><span>{s["pct"]}%</span></div>'
    f'<div class="track"><i style="width:{s["pct"]}"></i></div></div>' for s in slots) or \
    '<div class="slot"><div class="top"><b>待解锁</b><span>—</span></div><div class="track"><i style="width:2%"></i></div></div>'
timeline_html = "".join(
    f'<div class="item"><div class="when">{esc(t["when"])}</div>'
    f'<div class="what">{esc(t["what"])}</div></div>' for t in timeline) or \
    '<div class="item"><div class="when">—</div><div class="what">你的麦门故事还没开始写</div></div>'

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>麦门年鉴 {S.get("period",{}).get("label","")} · 你的麦门回忆录</title>
<style>
  :root{{--bg:#141210;--card:#1f1c18;--card2:#282420;--m-red:#DA291C;--m-gold:#FFC72C;--txt:#f5efe4;--sub:#a89c88;--line:rgba(255,199,44,.14);--radius:18px}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:var(--bg);color:var(--txt);font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.6;overflow-x:hidden}}
  .wrap{{max-width:760px;margin:0 auto;padding:48px 20px 80px}}
  .hero{{text-align:center;padding:36px 0 44px}}
  .hero .year{{font-size:15px;letter-spacing:.5em;color:var(--m-gold);text-transform:uppercase}}
  .hero h1{{font-size:56px;font-weight:900;margin:14px 0 6px;letter-spacing:.06em}}
  .hero h1 .gold{{color:var(--m-gold)}}
  .hero .sub{{color:var(--sub);font-size:15px}}
  .hero .arch{{width:120px;height:60px;margin:26px auto 0;position:relative}}
  .hero .arch::before{{content:"";position:absolute;inset:0;border:6px solid var(--m-gold);border-bottom:none;border-radius:120px 120px 0 0}}
  .hero .arch::after{{content:"";position:absolute;left:22px;right:22px;bottom:0;height:6px;background:var(--m-red);border-radius:3px}}
  .persona{{display:inline-block;margin-top:30px;padding:10px 26px;background:linear-gradient(135deg,var(--m-red),#a81e14);border-radius:999px;font-weight:700;font-size:17px;box-shadow:0 6px 24px rgba(218,41,28,.35)}}
  .persona small{{display:block;font-size:12px;font-weight:400;color:rgba(255,255,255,.75);letter-spacing:.2em}}
  .section-title{{display:flex;align-items:baseline;gap:12px;margin:52px 0 18px}}
  .section-title .no{{font-size:13px;color:var(--m-gold);font-weight:800;letter-spacing:.15em}}
  .section-title h2{{font-size:22px;font-weight:800}}
  .grid{{display:grid;gap:14px}}
  .g2{{grid-template-columns:1fr 1fr}}.g3{{grid-template-columns:1fr 1fr 1fr}}
  @media(max-width:560px){{.g3{{grid-template-columns:1fr 1fr}}.hero h1{{font-size:40px}}}}
  .card{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:22px;transition:transform .2s,border-color .2s}}
  .card:hover{{transform:translateY(-3px);border-color:rgba(255,199,44,.4)}}
  .card .label{{font-size:13px;color:var(--sub)}}
  .card .value{{font-size:34px;font-weight:900;margin-top:4px}}
  .card .value .unit{{font-size:15px;font-weight:600;color:var(--sub);margin-left:2px}}
  .card .note{{font-size:12px;color:var(--sub);margin-top:6px}}
  .card.hot{{background:linear-gradient(145deg,#2b1512,var(--card));border-color:rgba(218,41,28,.4)}}
  .card.hot .value{{color:var(--m-red)}}
  .card.gold{{background:linear-gradient(145deg,#2b2410,var(--card));border-color:rgba(255,199,44,.45)}}
  .card.gold .value{{color:var(--m-gold)}}
  .chart{{display:flex;align-items:flex-end;gap:6px;height:150px;padding-top:10px}}
  .chart .bar{{flex:1;display:flex;flex-direction:column;align-items:center;gap:8px;height:100%;justify-content:flex-end}}
  .chart .bar i{{display:block;width:100%;max-width:34px;border-radius:6px 6px 2px 2px;background:linear-gradient(180deg,var(--m-gold),#8f6c10);min-height:4px}}
  .chart .bar.peak i{{background:linear-gradient(180deg,var(--m-red),#7c130c);box-shadow:0 0 18px rgba(218,41,28,.45)}}
  .chart .bar em{{font-style:normal;font-size:11px;color:var(--sub)}}
  .chart .bar b{{font-size:11px;color:var(--txt);font-weight:700}}
  .rank{{display:flex;flex-direction:column;gap:10px}}
  .rank .row{{display:flex;align-items:center;gap:14px;background:var(--card2);border-radius:12px;padding:13px 16px}}
  .rank .row .no{{width:30px;height:30px;border-radius:8px;flex:none;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:14px;background:#3a332a;color:var(--sub)}}
  .rank .row:nth-child(1) .no{{background:var(--m-gold);color:#241a02}}
  .rank .row:nth-child(2) .no{{background:#c9c2b4;color:#241a02}}
  .rank .row:nth-child(3) .no{{background:#a9744a;color:#241a02}}
  .rank .row .name{{flex:1;font-weight:600}}
  .rank .row .cnt{{font-weight:800;color:var(--m-gold)}}
  .rank .row .bar-bg{{flex:1.4;height:8px;background:#332d25;border-radius:4px;overflow:hidden}}
  .rank .row .bar-bg i{{display:block;height:100%;background:var(--m-red);border-radius:4px}}
  .slots{{display:flex;flex-direction:column;gap:12px}}
  .slot .top{{display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px}}
  .slot .top b{{font-weight:700}}
  .slot .track{{height:10px;background:#332d25;border-radius:5px;overflow:hidden}}
  .slot .track i{{display:block;height:100%;border-radius:5px;background:var(--m-gold)}}
  .slot:nth-child(2) .track i{{background:var(--m-red)}}
  .timeline{{border-left:2px solid var(--line);margin-left:8px;padding-left:22px;display:flex;flex-direction:column;gap:20px}}
  .timeline .item{{position:relative}}
  .timeline .item::before{{content:"";position:absolute;left:-29px;top:6px;width:12px;height:12px;border-radius:50%;background:var(--m-gold);box-shadow:0 0 0 4px rgba(255,199,44,.15)}}
  .timeline .when{{font-size:12px;color:var(--sub)}}
  .timeline .what{{font-weight:700;margin-top:2px}}
  .title-card{{text-align:center;background:linear-gradient(160deg,#2a1a08,#1f1c18 60%);border:1px solid rgba(255,199,44,.4);border-radius:var(--radius);padding:38px 24px}}
  .title-card .big{{font-size:30px;font-weight:900;color:var(--m-gold)}}
  .title-card .desc{{color:var(--sub);margin-top:10px;font-size:14px}}
  .title-card .lv{{margin-top:18px;display:inline-flex;align-items:center;gap:8px;font-size:13px;color:var(--sub)}}
  .lv .pill{{background:var(--m-red);color:#fff;font-weight:800;border-radius:999px;padding:3px 12px}}
  footer{{margin-top:60px;text-align:center;color:var(--sub);font-size:12px;line-height:2}}
  footer .demo-tag{{display:inline-block;background:#3a332a;border-radius:6px;padding:2px 10px;color:var(--m-gold);font-weight:700;letter-spacing:.1em;margin-bottom:8px}}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="year">Maimen Memoir · {esc(S.get("period",{}).get("label","2026"))}</div>
    <h1>麦门<span class="gold">年鉴</span></h1>
    <div class="arch"></div>
    <div class="persona"><small>YOUR PERSONA</small>{esc(title.get("name") or "准麦门新人")}</div>
    <p class="sub" style="margin-top:18px">{esc(hero_sub)}</p>
  </header>

  <div class="section-title"><span class="no">01</span><h2>这一年的数字</h2></div>
  <div class="grid g3">
    <div class="card hot"><div class="label">订单数</div><div class="value">{T.get("orders",0)}<span class="unit">单</span></div><div class="note">{"平均每 " + str(round(365 / max(T.get("orders",1),1), 1)) + " 天吃一次麦麦" if not empty else "第一单从这里开始"}</div></div>
    <div class="card gold"><div class="label">总消费</div><div class="value">¥{T.get("spend",0)}<span class="unit"></span></div><div class="note">钱没有消失，只是变成了麦门信仰</div></div>
    <div class="card"><div class="label">当前可用积分</div><div class="value">{S.get("account",{}).get("available","0")}<span class="unit">分</span></div><div class="note">{"本月将过期 " + S.get("account",{}).get("expiring","0") + " 分，别浪费" if S.get("account",{}).get("expiring","0") != "0" else "攒着换好物"}</div></div>
  </div>
  <div class="grid g2" style="margin-top:14px">
    <div class="card"><div class="label">最常吃的</div><div class="value" style="font-size:24px">{esc(T.get("top_item") or "待解锁")} {("× " + str(T.get("top_item_cnt"))) if T.get("top_item") else ""}</div><div class="note">你的年度本命麦麦</div></div>
    <div class="card"><div class="label">最常去的门店</div><div class="value" style="font-size:24px">{esc(T.get("top_store") or "待解锁")}</div><div class="note">{(str(T.get("top_store_cnt")) + " 次光顾 · 店员都认识你了") if T.get("top_store") else "下一单就会诞生你的据点"}</div></div>
  </div>

  <div class="section-title"><span class="no">02</span><h2>每个月的麦门浓度</h2></div>
  <div class="card"><div class="chart">{months_html}</div>
  <p class="note" style="margin-top:14px">{"📈 峰值在 " + next((m["m"] for m in months if m["n"] == peak), "") + "——" + str(peak) + " 单，麦麦对你是刚需" if peak else "📊 空白画布，等你涂满金黄"}</p></div>

  <div class="section-title"><span class="no">03</span><h2>口味档案 · TOP 5</h2></div>
  <div class="card"><div class="rank">{tops_html}</div></div>

  <div class="section-title"><span class="no">04</span><h2>时间画像</h2></div>
  <div class="card"><div class="slots">{slots_html}</div>
  <p class="note" style="margin-top:14px">{"🌙 你的订单有时段偏好——生物钟诚实得很" if slots else "🕐 下单时间会暴露你是哪种麦门人"}</p></div>

  <div class="section-title"><span class="no">05</span><h2>麦门大事记</h2></div>
  <div class="timeline">{timeline_html}</div>

  <div class="section-title"><span class="no">06</span><h2>年度麦门认证</h2></div>
  <div class="title-card">
    <div class="big">「 {esc(title.get("name") or "准麦门新人")} 」</div>
    <p class="desc">{esc(title.get("desc") or "还没有订单？第一单就是圣典的第一页。")}</p>
    <div class="lv"><span class="pill">Lv.{title.get("lv",0)}</span>{esc(title.get("next") or "麦门段位 · 待定级")}</div>
  </div>

  <footer>
    <div>{('<span class="demo-tag">DEMO 数据 · 非真实消费记录</span>' if mock else "")}</div>
    <div>由 <a href="https://github.com/qinaction/maimen-memoir" target="_blank" rel="noopener noreferrer" style="color:var(--m-gold);text-decoration:none">maimen-memoir</a> 生成 · 数据来源：麦当劳中国 MCP Server · {esc(S.get("generated_at",""))}</div>
    <div>非麦当劳官方产品 · 餐品与活动信息以官方渠道为准</div>
  </footer>
</div>
</body>
</html>'''

open(OUT_PATH, "w", encoding="utf-8").write(html)
print(f"[ok] -> {OUT_PATH}")
