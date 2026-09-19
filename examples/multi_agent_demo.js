/**
 * AgentOS 2.0 — Multi-Agent Parallel Demo (Node.js)
 * Run multiple AgentOS skills in parallel using Promise.all
 * Usage: node multi_agent_demo.js
 */

const Anthropic = require("@anthropic-ai/sdk").default;
const fs = require("fs");
const path = require("path");

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const REPO_ROOT = path.join(__dirname, "..");

/**
 * Load a skill from its SKILL.md file
 * @param {string} skillName
 * @returns {string}
 */
function loadSkill(skillName) {
  const skillPath = path.join(REPO_ROOT, skillName, "SKILL.md");
  if (!fs.existsSync(skillPath)) {
    throw new Error(`Skill not found: ${skillName} (expected at ${skillPath})`);
  }
  return fs.readFileSync(skillPath, "utf-8");
}

/**
 * Activate a single skill and return the response
 * @param {string} skillName
 * @param {string} question
 * @returns {Promise<{skill: string, answer: string, tokens: number}>}
 */
async function activateSkill(skillName, question) {
  const skill = loadSkill(skillName);
  const start = Date.now();

  const response = await client.messages.create({
    model: "claude-sonnet-4-6",
    max_tokens: 4096,
    system: skill,
    messages: [{ role: "user", content: question }],
  });

  return {
    skill: skillName,
    answer: response.content[0].text,
    tokens: response.usage.input_tokens + response.usage.output_tokens,
    latencyMs: Date.now() - start,
  };
}

/**
 * AgentOS orchestration: run multiple skills in parallel
 */
async function runParallelAgents() {
  console.log("=== AgentOS 2.0 — Parallel Multi-Agent Demo ===\n");

  const tasks = [
    {
      skill: "quant-trader",
      question: "Generate a trade signal for NVDA. Include entry, target, stop, Kelly size.",
    },
    {
      skill: "risk-sentinel",
      question: "Calculate VaR 95% and CVaR for portfolio: 50% SPY, 30% QQQ, 20% TLT. Daily.",
    },
    {
      skill: "startup-advisor",
      question: "Review these metrics: ARR $2M, MoM growth 15%, CAC $800, LTV $3200, churn 4%.",
    },
  ];

  console.log(`Dispatching ${tasks.length} agents in parallel...\n`);
  const startAll = Date.now();

  // All skills run in parallel — same as AgentOS orchestrator pattern
  const results = await Promise.allSettled(
    tasks.map(({ skill, question }) => activateSkill(skill, question))
  );

  const totalMs = Date.now() - startAll;
  console.log(`Completed in ${totalMs}ms (parallel execution)\n`);
  console.log("=".repeat(60));

  results.forEach((result, i) => {
    const task = tasks[i];
    if (result.status === "fulfilled") {
      const { skill, answer, tokens, latencyMs } = result.value;
      console.log(`\n[${skill.toUpperCase()}] (${tokens} tokens, ${latencyMs}ms)`);
      console.log("-".repeat(50));
      // Print first 400 chars
      console.log(answer.slice(0, 400) + (answer.length > 400 ? "..." : ""));
    } else {
      console.log(`\n[${task.skill.toUpperCase()}] ERROR: ${result.reason.message}`);
    }
  });
}

/**
 * List all available AgentOS skills
 * @returns {string[]}
 */
function listSkills() {
  const EXCLUDED = new Set(["examples", "prompts", "template-skill", ".git"]);
  return fs
    .readdirSync(REPO_ROOT, { withFileTypes: true })
    .filter(
      (entry) =>
        entry.isDirectory() &&
        !EXCLUDED.has(entry.name) &&
        fs.existsSync(path.join(REPO_ROOT, entry.name, "SKILL.md"))
    )
    .map((entry) => entry.name)
    .sort();
}

// ── Main ──────────────────────────────────────────────────────────────────────
const skills = listSkills();
console.log(`AgentOS 2.0 — ${skills.length} skills ready`);
console.log("Set ANTHROPIC_API_KEY to run demos.\n");

if (process.env.ANTHROPIC_API_KEY) {
  runParallelAgents().catch(console.error);
} else {
  console.log("Available skills:\n");
  console.log(skills.join("\n"));
}
