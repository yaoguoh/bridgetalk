/**
 * Skill Activation Prompt Hook
 *
 * 在用户提交 prompt 时自动匹配并建议相关 Skill
 *
 * 触发时机: UserPromptSubmit
 */

import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

// 获取当前文件目录
const __dirname = dirname(fileURLToPath(import.meta.url));

// 类型定义
interface HookInput {
  session_id: string;
  prompt: string;
  working_directory?: string;
  recent_files?: string[];
}

interface SkillTriggers {
  keywords?: string[];
  intentPatterns?: string[];
  pathPatterns?: string[];
  contentPatterns?: string[];
}

interface SkillRule {
  type: "domain" | "command";
  priority: "critical" | "high" | "medium" | "low";
  description: string;
  triggers: SkillTriggers;
}

interface SkillRules {
  version: string;
  skills: Record<string, SkillRule>;
}

interface MatchResult {
  skillName: string;
  rule: SkillRule;
  matchedKeywords: string[];
  matchedPatterns: string[];
  score: number;
}

// 优先级权重
const PRIORITY_WEIGHTS: Record<string, number> = {
  critical: 100,
  high: 75,
  medium: 50,
  low: 25,
};

// 读取 skill-rules.json
function loadSkillRules(): SkillRules | null {
  const rulesPath = join(__dirname, "../skills/skill-rules.json");
  if (!existsSync(rulesPath)) {
    return null;
  }
  try {
    const content = readFileSync(rulesPath, "utf-8");
    return JSON.parse(content) as SkillRules;
  } catch {
    return null;
  }
}

// 关键词匹配
function matchKeywords(prompt: string, keywords: string[]): string[] {
  const lowerPrompt = prompt.toLowerCase();
  return keywords.filter((kw) => lowerPrompt.includes(kw.toLowerCase()));
}

// 意图模式匹配
function matchIntentPatterns(prompt: string, patterns: string[]): string[] {
  const matched: string[] = [];
  for (const pattern of patterns) {
    try {
      const regex = new RegExp(pattern, "i");
      if (regex.test(prompt)) {
        matched.push(pattern);
      }
    } catch {
      // 无效正则，跳过
    }
  }
  return matched;
}

// 计算匹配分数
function calculateScore(
  matchedKeywords: string[],
  matchedPatterns: string[],
  priority: string
): number {
  const keywordScore = matchedKeywords.length * 10;
  const patternScore = matchedPatterns.length * 20;
  const priorityScore = PRIORITY_WEIGHTS[priority] || 0;
  return keywordScore + patternScore + priorityScore;
}

// 匹配所有 Skill
function matchSkills(input: HookInput, rules: SkillRules): MatchResult[] {
  const results: MatchResult[] = [];

  for (const [skillName, rule] of Object.entries(rules.skills)) {
    const matchedKeywords = rule.triggers.keywords
      ? matchKeywords(input.prompt, rule.triggers.keywords)
      : [];

    const matchedPatterns = rule.triggers.intentPatterns
      ? matchIntentPatterns(input.prompt, rule.triggers.intentPatterns)
      : [];

    // 只要有任何匹配就记录
    if (matchedKeywords.length > 0 || matchedPatterns.length > 0) {
      const score = calculateScore(
        matchedKeywords,
        matchedPatterns,
        rule.priority
      );
      results.push({
        skillName,
        rule,
        matchedKeywords,
        matchedPatterns,
        score,
      });
    }
  }

  // 按分数排序
  return results.sort((a, b) => b.score - a.score);
}

// 格式化输出
function formatOutput(matches: MatchResult[]): string {
  if (matches.length === 0) {
    return "";
  }

  const lines: string[] = [
    "",
    "╔══════════════════════════════════════════════════════════════╗",
    "║                   🎯 SKILL ACTIVATION CHECK                  ║",
    "╚══════════════════════════════════════════════════════════════╝",
    "",
  ];

  // 按优先级分组
  const grouped: Record<string, MatchResult[]> = {
    critical: [],
    high: [],
    medium: [],
    low: [],
  };

  for (const match of matches) {
    const priority = match.rule.priority;
    if (grouped[priority]) {
      grouped[priority].push(match);
    }
  }

  const labels: Record<string, string> = {
    critical: "🔴 CRITICAL (Required)",
    high: "🟠 HIGH (Recommended)",
    medium: "🟡 MEDIUM (Suggested)",
    low: "🟢 LOW (Optional)",
  };

  for (const [priority, label] of Object.entries(labels)) {
    const group = grouped[priority];
    if (group && group.length > 0) {
      lines.push(`${label}:`);
      for (const match of group) {
        lines.push(`  → /${match.skillName}: ${match.rule.description}`);
        if (match.matchedKeywords.length > 0) {
          lines.push(`    匹配关键词: ${match.matchedKeywords.join(", ")}`);
        }
      }
      lines.push("");
    }
  }

  lines.push("────────────────────────────────────────────────────────────────");
  lines.push("");

  return lines.join("\n");
}

// 主函数
async function main() {
  // 从 stdin 读取输入
  let inputData = "";
  for await (const chunk of process.stdin) {
    inputData += chunk;
  }

  if (!inputData.trim()) {
    return;
  }

  let input: HookInput;
  try {
    input = JSON.parse(inputData);
  } catch {
    // 无效 JSON，静默退出
    return;
  }

  // 加载规则
  const rules = loadSkillRules();
  if (!rules) {
    return;
  }

  // 匹配 Skill
  const matches = matchSkills(input, rules);

  // 输出结果
  const output = formatOutput(matches);
  if (output) {
    process.stdout.write(output);
  }
}

main().catch(() => {
  // 静默处理错误
});
