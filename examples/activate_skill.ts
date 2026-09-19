/**
 * AgentOS 2.0 — Universal Skill Activator (TypeScript)
 * Activate any AgentOS skill via the Claude API
 */
import Anthropic from "@anthropic-ai/sdk";
import * as fs from "fs";
import * as path from "path";

const client = new Anthropic();

interface SkillResponse {
  skill: string;
  question: string;
  answer: string;
  inputTokens: number;
  outputTokens: number;
}

async function loadSkill(skillName: string): Promise<string> {
  const skillPath = path.join(__dirname, "..", skillName, "SKILL.md");
  return fs.readFileSync(skillPath, "utf-8");
}

async function activateSkill(
  skillName: string,
  question: string,
  model: string = "claude-sonnet-4-6"
): Promise<SkillResponse> {
  const skill = await loadSkill(skillName);

  const response = await client.messages.create({
    model,
    max_tokens: 8096,
    system: skill,
    messages: [{ role: "user", content: question }],
  });

  const content = response.content[0];
  if (content.type !== "text") throw new Error("Unexpected response type");

  return {
    skill: skillName,
    question,
    answer: content.text,
    inputTokens: response.usage.input_tokens,
    outputTokens: response.usage.output_tokens,
  };
}

// Demo: Activate CEOWarRoom for a strategic decision
async function ceoWarRoomDemo(): Promise<void> {
  console.log("=== CEOWarRoom: Strategic Decision Analysis ===\n");

  const result = await activateSkill(
    "ceo-war-room",
    `Our Series B SaaS company ($8M ARR, growing 120% YoY) just received
     an acquisition offer for $80M. We could also raise a Series C at $120M valuation.
     Run the CEOWarRoom capital allocation framework. What should we do?`
  );

  console.log(`Skill: ${result.skill}`);
  console.log(`Tokens used: ${result.inputTokens} in / ${result.outputTokens} out\n`);
  console.log(result.answer);
}

// Demo: Multi-skill parallel activation
async function multiSkillDemo(): Promise<void> {
  console.log("=== AgentOS: Multi-Skill Parallel Analysis ===\n");

  const tasks = [
    { skill: "quant-trader", q: "Give me a trade signal on NVDA with full risk analysis" },
    { skill: "risk-sentinel", q: "Run VaR analysis on a portfolio: 60% SPY, 30% QQQ, 10% BTC" },
    { skill: "startup-advisor", q: "Review our unit economics: CAC $450, LTV $2100, churn 3% monthly" },
  ];

  const results = await Promise.all(
    tasks.map(({ skill, q }) => activateSkill(skill, q))
  );

  results.forEach((r) => {
    console.log(`\n--- ${r.skill.toUpperCase()} ---`);
    console.log(r.answer.slice(0, 500) + "...\n");
  });
}

// Skill availability checker
async function listAvailableSkills(): Promise<string[]> {
  const repoRoot = path.join(__dirname, "..");
  const entries = fs.readdirSync(repoRoot, { withFileTypes: true });

  return entries
    .filter((e) => e.isDirectory() && fs.existsSync(path.join(repoRoot, e.name, "SKILL.md")))
    .map((e) => e.name)
    .filter((n) => !["examples", "prompts", "template-skill"].includes(n))
    .sort();
}

async function main(): Promise<void> {
  const skills = await listAvailableSkills();
  console.log(`AgentOS 2.0 — ${skills.length} skills available:\n`);
  console.log(skills.join("  ·  "));
  console.log("\nSet ANTHROPIC_API_KEY and uncomment a demo to run.");

  // Uncomment to run:
  // await ceoWarRoomDemo();
  // await multiSkillDemo();
}

main().catch(console.error);
