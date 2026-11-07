# -*- coding: utf-8 -*-
"""Dumate 每日签到包装（pythonw 静默）：cwd 中文路径由 python 处理，node --once --only=dumate，
输出追加 dumate_checkin.log。凭据由 daily-checkin.js 自动读本机客户端（不出本机）。"""
import os
import subprocess
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'dumate_checkin.log')

def main():
    os.chdir(HERE)
    with open(LOG, 'ab') as f:
        f.write(('===== ' + datetime.datetime.now().isoformat(timespec='seconds') + ' =====' + chr(10)).encode('utf-8'))
        r = subprocess.run(['node', 'daily-checkin.js', '--once', '--only=dumate'],
                           stdout=f, stderr=subprocess.STDOUT, timeout=180)
    sys.exit(r.returncode)

if __name__ == '__main__':
    main()
