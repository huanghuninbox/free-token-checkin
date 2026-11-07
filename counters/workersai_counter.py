# -*- coding: utf-8 -*-
"""Cloudflare Workers AI 本地计数器（free-token-checkin/counters）
原理：官方 analytics API 需要 Account Analytics 权限（普通 AI Token 查不了）——
      在调用侧自己记账：每次调用记录 tokens，按保守系数折算 neurons，
      汇总后与免费额度（10K neurons/天）对比，确保不浪费、不超额。
用法：直接 python workersai_counter.py "你的提示词"（等价于调用+记账）
汇总：counters/usage_summary.py 读 usage_log.jsonl 出当日用量。
"""
import sys
import os
import json
import urllib.request
import datetime

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workersai_usage_log.jsonl')
NEURON_PER_TOKEN = 0.01  # 保守估算：约 1K tokens ≈ 10 neurons（官方换算未公开）
DAILY_FREE_NEURONS = 10_000


def load_secrets():
    """密钥来源：环境变量 CF_API_TOKEN/CF_ACCOUNT_ID，或同目录 secrets.env（KEY=VALUE）"""
    env = {k: os.environ.get(k, '') for k in ('CF_API_TOKEN', 'CF_ACCOUNT_ID')}
    if all(env.values()):
        return env
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.env')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8', errors='replace'):
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                env[k] = v.strip().strip('"')
    return env


def log_usage(model, pin, pout):
    u = (pin or 0) + (pout or 0)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'ts': datetime.datetime.now().isoformat(timespec='seconds'),
                            'model': model, 'tokens_in': pin, 'tokens_out': pout,
                            'tokens': u, 'neurons_est': round(u * NEURON_PER_TOKEN, 1)}, ensure_ascii=False) + chr(10))


def today_usage():
    today = datetime.date.today().isoformat()
    calls = tokens = neurons = 0
    if os.path.exists(LOG):
        for line in open(LOG, encoding='utf-8', errors='replace'):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if str(r.get('ts', ''))[:10] == today:
                calls += 1
                tokens += r.get('tokens', 0) or 0
                neurons += r.get('neurons_est', 0) or 0
    return calls, tokens, neurons


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        calls, tokens, neurons = today_usage()
        print(f'今日用量：{calls} 次 ≈ {neurons:.1f} neurons（估）/ {DAILY_FREE_NEURONS}，累计 {tokens} tokens')
        print('调用：python workersai_counter.py "提示词" [--model @cf/meta/llama-3.2-3b-instruct]')
        return
    prompt = sys.argv[1]
    model = '@cf/meta/llama-3.2-3b-instruct'
    if '--model' in sys.argv:
        model = sys.argv[sys.argv.index('--model') + 1]
    s = load_secrets()
    body = json.dumps({'model': model, 'messages': [{'role': 'user', 'content': prompt}],
                       'max_tokens': 2048}).encode('utf-8')
    req = urllib.request.Request(
        'https://api.cloudflare.com/client/v4/accounts/' + s['CF_ACCOUNT_ID'] + '/ai/v1/chat/completions',
        data=body, headers={'Authorization': 'Bearer ' + s['CF_API_TOKEN'], 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    out = (d['choices'][0]['message'].get('content') or '').strip()
    u = (d.get('usage') or {})
    log_usage(model, u.get('prompt_tokens', 0), u.get('completion_tokens', 0))
    calls, tokens, neurons = today_usage()
    print(out)
    print(f'—— 今日 {calls} 次 ≈ {neurons:.1f}/10000 neurons ——')


if __name__ == '__main__':
    main()
