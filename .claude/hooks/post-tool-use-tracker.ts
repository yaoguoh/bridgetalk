/**
 * Post Tool Use Tracker Hook
 *
 * 追踪 Edit/Write/MultiEdit 修改的文件
 *
 * 触发时机: PostToolUse (matcher: Edit|MultiEdit|Write)
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync } from "fs";
import { join, dirname, relative } from "path";
import { fileURLToPath } from "url";
import { tmpdir } from "os";

// 获取当前文件目录
const __dirname = dirname(fileURLToPath(import.meta.url));

// 类型定义
interface ToolInput {
  file_path?: string;
  path?: string;
  edits?: Array<{ file_path: string }>;
}

interface HookInput {
  session_id: string;
  tool: string;
  tool_input: ToolInput;
}

interface TrackedSession {
  session_id: string;
  modified_files: string[];
  project_areas: string[];
  last_updated: string;
}

// 项目区域检测规则 - 适配 bridgetalk 项目结构
const PROJECT_AREAS: Record<string, RegExp[]> = {
  backend: [
    /apps\/backend\//,
    /src\/domain\//,
    /src\/core\//,
    /\.py$/,
  ],
  frontend: [/apps\/frontend\//, /\.tsx?$/, /\.jsx?$/],
  config: [/\.json$/, /\.yaml$/, /\.yml$/, /\.toml$/],
  docs: [/docs\//, /\.md$/],
  tests: [/tests?\//, /\.test\.[tj]sx?$/, /\.spec\.[tj]sx?$/],
};

// 获取追踪文件路径
function getTrackerFilePath(sessionId: string): string {
  const trackerDir = join(tmpdir(), "claude-code-tracker");
  if (!existsSync(trackerDir)) {
    mkdirSync(trackerDir, { recursive: true });
  }
  return join(trackerDir, `session-${sessionId}.json`);
}

// 加载会话追踪数据
function loadSession(sessionId: string): TrackedSession {
  const filePath = getTrackerFilePath(sessionId);
  if (existsSync(filePath)) {
    try {
      const content = readFileSync(filePath, "utf-8");
      return JSON.parse(content) as TrackedSession;
    } catch {
      // 文件损坏，重新创建
    }
  }
  return {
    session_id: sessionId,
    modified_files: [],
    project_areas: [],
    last_updated: new Date().toISOString(),
  };
}

// 保存会话追踪数据
function saveSession(session: TrackedSession): void {
  const filePath = getTrackerFilePath(session.session_id);
  session.last_updated = new Date().toISOString();
  writeFileSync(filePath, JSON.stringify(session, null, 2));
}

// 从工具输入中提取文件路径
function extractFilePaths(toolInput: ToolInput): string[] {
  const paths: string[] = [];

  // Edit/Write 工具
  if (toolInput.file_path) {
    paths.push(toolInput.file_path);
  }
  if (toolInput.path) {
    paths.push(toolInput.path);
  }

  // MultiEdit 工具
  if (toolInput.edits && Array.isArray(toolInput.edits)) {
    for (const edit of toolInput.edits) {
      if (edit.file_path) {
        paths.push(edit.file_path);
      }
    }
  }

  return paths;
}

// 检测项目区域
function detectProjectAreas(filePath: string): string[] {
  const areas: string[] = [];
  for (const [area, patterns] of Object.entries(PROJECT_AREAS)) {
    for (const pattern of patterns) {
      if (pattern.test(filePath)) {
        areas.push(area);
        break;
      }
    }
  }
  return areas;
}

// 格式化输出
function formatOutput(session: TrackedSession, newFiles: string[]): string {
  if (newFiles.length === 0) {
    return "";
  }

  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const lines: string[] = ["", "📝 文件修改追踪:"];

  for (const file of newFiles) {
    const relativePath = relative(projectDir, file);
    const areas = detectProjectAreas(relativePath);
    const areaTag = areas.length > 0 ? ` [${areas.join(", ")}]` : "";
    lines.push(`  → ${relativePath}${areaTag}`);
  }

  if (session.modified_files.length > newFiles.length) {
    const total = session.modified_files.length;
    lines.push(`  (本会话共修改 ${total} 个文件)`);
  }

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

  // 确保有 session_id
  if (!input.session_id) {
    return;
  }

  // 提取文件路径
  const filePaths = extractFilePaths(input.tool_input);
  if (filePaths.length === 0) {
    return;
  }

  // 加载会话
  const session = loadSession(input.session_id);

  // 添加新文件（去重）
  const newFiles: string[] = [];
  for (const filePath of filePaths) {
    if (!session.modified_files.includes(filePath)) {
      session.modified_files.push(filePath);
      newFiles.push(filePath);

      // 更新项目区域
      const areas = detectProjectAreas(filePath);
      for (const area of areas) {
        if (!session.project_areas.includes(area)) {
          session.project_areas.push(area);
        }
      }
    }
  }

  // 保存会话
  saveSession(session);

  // 输出结果
  const output = formatOutput(session, newFiles);
  if (output) {
    process.stdout.write(output);
  }
}

main().catch(() => {
  // 静默处理错误
});
