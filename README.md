# free-token-checkin

> 多平台 AI 编程工具的**每日签到 + 免费额度确认**工具集。签到领积分、计数器盯用量、一张表查清「每个端口还剩多少、什么时候过期」。

English: free-token-checkin is a toolset that automates daily check-ins for multiple AI coding platforms, including WorkBuddy, Trae, and DuMate. It also provides a local usage counter for Cloudflare Workers AI and Zhipu resource packs, filling the gap left by the absence of official balance APIs. Built-in expiration alerts warn you before your points lapse, so you never waste unused quota.

> （本段英文简介由 buddy 端 glm-5.3-flash 生成——免费算力实操示范，2026-11-07）

## 覆盖平台矩阵

| 平台 | 签到 | 额度确认 | 实现来源 |
|---|---|---|---|
| WorkBuddy（腾讯） | ✅ 每日 +100（成长中心全套+补签） | 签到日志解析 | [88lin/workbuddy-auto-signin](checkins/workbuddy)（MIT） |
| Trae（字节） | ✅ 每日签到 + **积分余额/到期包监控** | `trae_credit_monitor.py`（余额+最早到期包） | [L0NE-6/Trae-AutoCheckin](checkins/trae)（MIT） |
| DuMate（百度搭子） | ✅ 每日 1000 积分 | 签到日志 | [Wang-JQ77/daily-auto-checkin](checkins/dumate)（MIT，本库收录 DuMate 模块） |
| Cloudflare Workers AI | —（无签到） | **本地计数器**：每次调用记 tokens→neurons 估算 | 自写 [counters/workersai_counter.py](counters/workersai_counter.py) |
| 智谱 BigModel | —（资源包制） | **本地计数器**：自基线递减出估算剩余 | 自写 [counters/glmfree_counter.py](counters/glmfree_counter.py) |

## 为什么需要「额度确认」

2026 年各家免费政策收紧飞快：宣传页说的和实际能用的差距很大（免费档突然要正余额、CLI 免费层直接砍停、积分包静默过期）。本工具集的原则：

1. **签到类全自动**——挂计划任务每天领，错过补签
2. **用量类本地计数**——官方不给余额 API 的（Cloudflare/智谱资源包），在调用侧自己记账，剩余量自基线递减
3. **过期类主动报警**——积分包到期日在监控日志里显式标注（如 Trae 的「最早到期包 2026-11-14 剩 75.55」），不浪费每一分额度

## 快速开始

```bash
# 1. 选平台进入目录，按各自 README 配置凭据（均支持从本机客户端自动提取登录态）
cd checkins/trae
python trae_get_token.py        # 从 Trae 客户端一键提取 Token（零依赖、不联网）

# 2. 挂计划任务（Windows 示例：每天 00:10 签到+监控）
# 见各目录 README 的「计划任务」节

# 3. 额度计数器（无官方 API 的平台）
python counters/workersai_counter.py   # 包装调用+记账
python counters/glmfree_counter.py     # 同上
```

## 额度确认方式矩阵（实测精华）

见 [docs/quota-matrix.md](docs/quota-matrix.md)——每个平台的余额查询方式、坑与替代方案（含「宣传 vs 实测」对照）。

## 目录结构

```
checkins/          # 签到工具（按平台分目录，各自带 LICENSE 与 README）
  workbuddy/ trae/ dumate/
counters/          # 本地用量计数器（自写，零依赖）
docs/              # 额度确认方式矩阵等文档
```

## 致谢与许可

- [88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin)、[L0NE-6/Trae-AutoCheckin](https://github.com/L0NE-6/Trae-AutoCheckin)、[Wang-JQ77/daily-auto-checkin](https://github.com/Wang-JQ77/daily-auto-checkin) ——各目录内保留原作者 LICENSE/NOTICE，感谢开源
- `counters/` 与 `docs/` 为本项目自写，MIT

## License

各子目录遵循其原始许可（均 MIT）；本项目新增部分 [MIT](LICENSE)。
