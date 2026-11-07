# -*- coding: utf-8 -*-
"""智谱 BigModel 资源包本地计数器（free-token-checkin/counters）
原理：资源包类账户无公开余额 API（实测 /users/me/balance 404；社区 cc-switch issue 同证）——
      调用侧自己记账：每次调用记 total_tokens，自基线递减出估算剩余。
      精确余量以 BigModel 控制台资源包页为准。
用法：python glmfree_counter.py "你的提示词"（等价于调用+记账）
      python glmfree_counter.py --usage  （只看当日/累计/估算剩余）
"""
import sys
import os
import json
import urllib.request
import datetime

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glmfree_usage_log.jsonl')
BASELINE_TOKENS = 40_000_000  # 资源包基线（按自己控制台的实际余量改）


def load_key():
    key = os.environ.get('GLMFREE_KEY', '')
    if key:
        return key
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.env')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8', errors='replace'):
            if line.strip().startswith('GLMFREE_KEY='):
                return line.strip().split('=', 1)[1].strip().strip('"')
    raise SystemExit('未配置 GLMFREE_KEY（环境变量或 secrets.env）')


def read_log():
    total = today = 0
    t0 = datetime.date.today().isoformat()
    if os.path.exists(LOG):
        for line in open(LOG, encoding='utf-8', errors='replace'):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            total += r.get('total_tokens', 0) or 0
            if str(r.get('ts', ''))[:10] == t0:
                today += r.get('total_tokens', 0) or 0
    return total, today


def main():
    if '--usage' in sys.argv:
        total, today = read_log()
        remain = max(0, BASELINE_TOKENS - total)
        print(f'今日 {today} tokens；自基线计剩余 ≈{remain / 10000:.0f} 万（{BASELINE_TOKENS // 10000} 万-已计 {total}，控制台为准）')
        return
    prompt = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    body = json.dumps({'model': os.environ.get('GLMFREE_MODEL', 'glm-5.3-flash'),
                       'messages': [{'role': 'user', 'content': prompt}],
                       'max_tokens': 4096}).encode('utf-8')
    req = urllib.request.Request('https://open.bigmodel.cn/api/paas/v4/chat/completions',
                                 data=body,
                                 headers={'Authorization': 'Bearer ' + load_key(), 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    out = (d['choices'][0]['message'].get('content') or '').strip()
    if not out:
        raise SystemExit('empty reply')
    u = (d.get('usage') or {})
    rec = {'ts': datetime.datetime.now().isoformat(timespec='seconds'), 'model': d.get('model', 'glm'),
           'prompt_tokens': u.get('prompt_tokens', 0), 'completion_tokens': u.get('completion_tokens', 0),
           'total_tokens': u.get('total_tokens', 0)}
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + chr(10))
    total, today = read_log()
    remain = max(0, BASELINE_TOKENS - total)
    print(out)
    print(f'—— 今日 {today} tokens；估算剩余 ≈{remain / 10000:.0f} 万 ——')


if __name__ == '__main__':
    main()
