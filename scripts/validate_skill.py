#!/usr/bin/env python3
"""Validate bone-social-media-ops structure and safety invariants."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

required = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "NOTICE",
    "references/core-compliance.md",
    "references/xiaohongshu.md",
    "references/project-profile.md",
    "references/review-and-publish.md",
    "references/extension-contracts.md",
    "references/cold-start-and-account-analysis.md",
    "references/operating-plan-and-okr-loop.md",
    "references/content-archive.md",
    "references/performance-data-governance.md",
    "references/cross-channel-acquisition-analysis.md",
    "assets/project-profile-template.md",
    "assets/operating-plan-and-okr-template.md",
    "assets/content-brief-template.md",
    "assets/compliance-report-template.md",
    "assets/publish-package-template.md",
    "evals/evals.json",
    "evals/trigger-evals.json",
]

for relative in required:
    if not (ROOT / relative).is_file():
        errors.append(f"missing: {relative}")

skill_path = ROOT / "SKILL.md"
skill = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
if not re.match(r"^---\n.*?\n---\n", skill, re.S):
    errors.append("SKILL.md frontmatter missing or malformed")
else:
    frontmatter = skill.split("---", 2)[1]
    for field in ("name:", "description:"):
        if field not in frontmatter:
            errors.append(f"frontmatter missing {field}")
    if "name: bone-social-media-ops" not in frontmatter:
        errors.append("unexpected skill name")

if len(skill.splitlines()) > 500:
    errors.append("SKILL.md exceeds 500 lines")

for match in re.findall(r"`((?:references|assets)/[^`]+)`", skill):
    if not (ROOT / match).is_file():
        errors.append(f"broken local reference: {match}")

combined = "\n".join(
    p.read_text(encoding="utf-8")
    for p in ROOT.rglob("*.md")
    if p.is_file()
)
for phrase in (
    "用户明确确认",
    "内容发生实质变化时重新确认",
    "不无人值守发布笔记",
    "不自动评论、私信",
    "不承诺过审",
    "每一期发文建立完整内容包",
    "不得把发布不足、后台延迟或个位数样本直接解释为限流",
    "新号必须先养若干天",
    "未知、平台未提供、暂不可得统一视为 `null`",
    "不同生命周期的最新快照只能称为“已知规模”",
    "决策摘要 → 数据健康 → 表现趋势 → 同生命周期对照 → 文章拆解 → 漏斗诊断 → 行动与实验",
    "本轮不同时改",
    "诊断层级",
    "title_promise",
    "App Store 自然搜索/浏览",
    "不得把 Correlated 写成 Direct",
    "Apple Ads 广告搜索词报告不自动等同于全市场热词榜",
    "完整 ASO、广告投放或产品经营分析",
    "每次本 Skill 触发时，在执行当前任务前先恢复运营控制面",
    "计划—实际—判断—动作",
    "计划文档是策略事实源，Todo 是执行投影",
):
    if phrase not in combined:
        errors.append(f"missing safety invariant: {phrase}")

xhs = (ROOT / "references/xiaohongshu.md").read_text(encoding="utf-8") if (ROOT / "references/xiaohongshu.md").exists() else ""
for phrase in (
    "最近核验：2026-08-28",
    "B 级：平台官方来源",
    "笔记含 AI 合成内容",
    "AI创作者",
    "AI虚拟人",
    "自动回复评论、私信、群聊",
):
    if phrase not in xhs:
        errors.append(f"xiaohongshu rule missing: {phrase}")

# The public skill may mention Chebenben only in this validator comment? It should not
# embed project-specific facts in public instructions or templates.
for p in list((ROOT / "references").glob("*.md")) + list((ROOT / "assets").glob("*.md")) + [skill_path]:
    if p.exists() and "车本本" in p.read_text(encoding="utf-8"):
        errors.append(f"project-specific fact leaked into public skill: {p.relative_to(ROOT)}")

try:
    evals = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
    if evals.get("skill_name") != "bone-social-media-ops":
        errors.append("evals skill_name mismatch")
    behavior_evals = evals.get("evals", [])
    if len(behavior_evals) < 10:
        errors.append("fewer than 10 behavior evals")
    behavior_tags = {tag for item in behavior_evals for tag in item.get("tags", [])}
    required_behavior_tags = {
        "facts", "xiaohongshu", "rights", "privacy", "commercial-disclosure",
        "external-write", "automation", "cross-platform", "high-risk-domain", "page-change",
        "cold-start", "low-traffic", "analytics", "app-store", "cross-channel",
        "operating-plan", "okr", "progress-review",
    }
    for tag in sorted(required_behavior_tags - behavior_tags):
        errors.append(f"behavior eval coverage missing tag: {tag}")
except Exception as exc:
    errors.append(f"invalid evals.json: {exc}")

try:
    triggers = json.loads((ROOT / "evals/trigger-evals.json").read_text(encoding="utf-8"))
    if len(triggers) < 20:
        errors.append("fewer than 20 trigger evals")
    if not any(item.get("should_trigger") is True for item in triggers):
        errors.append("no positive trigger evals")
    if not any(item.get("should_trigger") is False for item in triggers):
        errors.append("no negative trigger evals")
    positive_text = "\n".join(item.get("query", "") for item in triggers if item.get("should_trigger") is True)
    negative_text = "\n".join(item.get("query", "") for item in triggers if item.get("should_trigger") is False)
    for keyword in ("小红书", "抖音", "评论", "自动", "竞品", "CSV"):
        if keyword not in positive_text:
            errors.append(f"positive trigger coverage missing keyword: {keyword}")
    for keyword in ("语法", "市场竞品", "提醒", "通用 CSV", "Obsidian"):
        if keyword not in negative_text:
            errors.append(f"negative trigger coverage missing keyword: {keyword}")
except Exception as exc:
    errors.append(f"invalid trigger-evals.json: {exc}")

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("VALIDATION PASSED")
print(f"root={ROOT}")
print(f"required_files={len(required)}")
print(f"skill_lines={len(skill.splitlines())}")
