# Bone Social Media Ops

Bone 的公共自媒体运营与合规 Skill。

## V1

- 正式支持：小红书
- 核心：项目内容档案、每期发文内容包、事实核验、AI/权益/平台审核、发布包、人工确认门禁
- 运营方法：账号状态分析、低流量诊断、冷启动内容实验、相同生命周期数据基线
- 后续接口：同品类调研、自有笔记指标、评论聚合与候选回复
- 不支持：无人值守自动发布、自动评论/私信、绕过平台限制、保证过审或保证流量

## 结构

- `SKILL.md`：触发与总工作流
- `references/core-compliance.md`：跨平台通用审核
- `references/xiaohongshu.md`：小红书官方规则包
- `references/project-profile.md`：项目事实档案方法
- `references/review-and-publish.md`：审核与两阶段发布门禁
- `references/extension-contracts.md`：调研、指标、评论和自动化扩展契约
- `references/cold-start-and-account-analysis.md`：小红书账号分析、低流量诊断与冷启动实验
- `references/content-archive.md`：Obsidian/运营资料库的每期发文归档规范
- `assets/`：项目档案、简报、审核、发布包模板
- `evals/`：行为和触发测试

## 验证

```bash
python3 scripts/validate_skill.py
```

平台规则会变化。更新规则包时同时记录来源、核验日期、变化点和受影响 eval。
