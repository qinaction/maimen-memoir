#!/usr/bin/env python3
"""
maimen-memoir 数据采集探针
通过 Streamable HTTP 调用麦当劳 MCP Server，采集年报所需的只读数据。
用法: MCD_TOKEN=xxx python3 collect.py <输出目录>
"""
import json
import os
import sys
import urllib.request

MCP_URL = "https://mcp.mcd.cn"
TOKEN = os.environ.get("MCD_TOKEN", "")
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "demo"
os.makedirs(OUT_DIR, exist_ok=True)

_id = 0


def _post(payload, session_id=None):
    """单次 JSON-RPC POST，返回 (parsed_body, session_id)"""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["mcp-session-id"] = session_id
    req = urllib.request.Request(MCP_URL, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        sid = resp.headers.get("mcp-session-id")
        raw = resp.read().decode()
    # 202 通知类响应返回空 body，直接返回 None
    if not raw.strip():
        return None, sid
    # SSE 帧只在响应以 data: 开头时解析；普通 JSON 可能内含 "data": 字样，不能盲切
    if raw.lstrip().startswith("data:"):
        raw = [l[5:].strip() for l in raw.splitlines() if l.startswith("data:")][-1]
    return json.loads(raw), sid


def call_tool(name, arguments=None):
    """初始化会话 → 调用工具。每次独立会话，避免状态残留"""
    global _id
    _id += 1
    _, sid = _post({
        "jsonrpc": "2.0", "id": 0, "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                   "clientInfo": {"name": "maimen-memoir", "version": "0.1.0"}},
    })
    _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    body, _ = _post({
        "jsonrpc": "2.0", "id": _id, "method": "tools/call",
        "params": {"name": name, "arguments": arguments or {}},
    }, sid)
    return body


# 年报数据源：全部只读工具，不碰下单/兑换/抽奖等写操作
TOOLS = [
    ("now-time-info", {}),
    ("query-my-account", {}),          # 积分账户：可用/累计/即将过期
    ("order-list", {}),                # 历史订单（到店+外送）
    ("query-my-coupons", {}),          # 我的优惠券
    ("mall-order-list", {}),           # 商城兑换订单
    ("query-my-prizes", {}),           # 积分抽奖奖品记录
    ("campaign-calendar", {}),         # 当月活动日历
    ("list-nutrition-foods", {}),      # 营养数据（用于餐品热量统计）
]

if __name__ == "__main__":
    for name, args in TOOLS:
        try:
            result = call_tool(name, args)
            path = os.path.join(OUT_DIR, f"{name}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            # 粗略判断是否业务报错
            txt = json.dumps(result, ensure_ascii=False)
            flag = "OK " if ("isError" not in txt or '"isError": false' in txt) else "ERR"
            print(f"[{flag}] {name} -> {path} ({len(txt)} bytes)")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
