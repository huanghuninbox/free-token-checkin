# -*- coding: utf-8 -*-
"""Trae 签到+积分监控 每日包装（run_trae.cmd → 本脚本 → 两上游脚本）。
凭据读同目录 .env.local（TRAE_ACCOUNTS 一行 JSON，本地留原位，95 区指针）；
输出追加 trae_daily.log（ledger_sync 解析「已用/剩余/最早到期包」进名册）。"""
import os
import subprocess
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'trae_daily.log')

def log(s):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(s + '\n')

def main():
    env_path = os.path.join(HERE, '.env.local')
    accounts = open(env_path, encoding='utf-8').readline().strip()
    env = dict(os.environ, TRAE_ACCOUNTS=accounts)
    log('===== %s =====' % datetime.datetime.now().isoformat(timespec='seconds'))
    for script in ('trae_checkin.py', 'trae_credit_monitor.py'):
        r = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           capture_output=True, text=True, encoding='utf-8', errors='replace',
                           env=env, cwd=HERE, timeout=300)
        for line in ((r.stdout or '') + (r.stderr or '')).splitlines():
            log(line)
    print('TRAE daily done')

if __name__ == '__main__':
    main()
