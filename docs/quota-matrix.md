# 额度确认方式矩阵（2026-11 实测）

> 每个 AI 平台的「余额怎么查」——宣传页说的和实际能用的，差距很大。本表全部为实测结论，持续更新。

## 实测对照表

| 平台 | 官方宣传 | 实测（2026-11） | 余额确认方式 |
|---|---|---|---|
| Cloudflare Workers AI | 免费 10K neurons/天 | ✅ 属实 | ❌ 无 AI 权限可读的用量 API（GraphQL 需 Account Analytics 权限）→ **本地计数器**（调用侧记账） |
| 智谱 GLM `glm-4.7-flash` | 永久免费档 | ⚠️ 属实但限流严（约 1-3 次/分，连发即 429） | ❌ 资源包类账户无余额 API（`/users/me/balance` 404，[cc-switch issue #4283](https://github.com/farion1231/cc-switch/issues/4283) 同证）→ **本地计数器**（基线递减） |
| 智谱资源包 | ≈4000 万 tokens | ✅ 可用（glm-5.3-flash 主力） | 同上：控制台精确查看 + 计数器估算 |
| CodeBuddy CLI | 与 IDE 共用积分池 | ✅ 无头模式可用，`--model` 支持免费/付费档 | ✅ 签到日志（余额随签到打印） |
| Trae | 积分制（Dollar Usage） | ✅ 每日签到 +100 | ✅ **非官方查询接口可用**（Trae-AutoCheckin 的 credit_monitor：余额+最早到期包） |
| DuMate（百度搭子） | 免费档每日 1000 积分 | ✅ 属实（限时活动） | 签到日志；客户端左下角礼物图标 |
| Gemini CLI | 免费层 1000 请求/天 | ❌ **已砍停**（2026-06 停服；替代品 preview 仅 20-50 请求/天，IneligibleTierError） | — |
| Qwen Code CLI | 免费 OAuth 档 | ❌ **已取消**（转订阅） | — |
| DeepSeek 网页版 | 免费对话额度 | ✅ 有，但无 API（官方余额 API 只覆盖 API 计费体系） | 网页人工（逆向 free-api 不建议：违反条款+封号风险） |
| Codex CLI（ChatGPT Plus） | 订阅额度 | ✅ 周限窗口（实测已用 59%/剩 41%） | ✅ 后端 API `chatgpt.com/backend-api/wham/usage`（本地 auth.json 的 access_token+`OpenAI-Beta: codex-1` 头；参考 [codex-reset-checker](https://github.com/doggy8088/codex-reset-checker)）；CLI 内 `/status` |
| 华为云 CodeArts | 积分模式（2026-09 起）+ 200 万 tokens 免费额度 | ✅ CLI headless 空壳（上游缺陷），GUI 可用 | 控制台「我的码道 > 套餐与用量」；BSS 费用中心 API 可自动化（需 AK/SK） |

## 核心教训

1. **fork 不作信息源**：监控上游清单时误用停更 fork（2026-04 起无提交），diff 全程失效三天才发现
2. **授权成功≠服务可用**：Gemini CLI OAuth 全程顺利，第一次真实调用才报 IneligibleTierError
3. **无 API 就自己记账**：Cloudflare/智谱都不给余额接口，调用侧计数器（基线递减）是最可靠的替代
4. **新源/新工具入列前必须实测 200**：网传「权威仓库」可能是错的仓库名（实测 404）
5. **CLI 通道先核版本受众**：TRAE CLI 装完才发现是企业版限定，个人版账号不能登录
