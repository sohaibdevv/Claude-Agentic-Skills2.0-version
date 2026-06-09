# Contributing to AgentOS 2.0

## Submitting a New Skill

### Requirements

1. **Real use case** — the skill must solve an actual problem, not a hypothetical one
2. **Tested** — verify the skill produces the intended behavior in at least Claude.ai and one other platform
3. **Original** — do not copy skills from other repositories without attribution
4. **Complete** — every skill must work standalone; no external dependencies assumed
5. **No PHI or secrets** — never include real patient data, API keys, or confidential information

### Skill Quality Bar

A skill is ready to submit when:
- It includes named sub-agents with distinct responsibilities
- It provides specific formulas, criteria, or thresholds — not just vague instructions
- It defines an output format with an example
- It states at least one forbidden behavior or constraint
- The `description` field clearly answers: "when should Claude use this skill?"

### Folder Naming

- lowercase, hyphen-separated: `my-new-skill`
- Descriptive of the domain and function: `climate-risk-analyst` not `climate`
- No version numbers in folder name

### File Structure

```
my-new-skill/
└── SKILL.md          (required)
    scripts/          (optional: executable scripts)
    references/       (optional: supplementary docs)
    assets/           (optional: templates, examples)
```

### SKILL.md Format

```markdown
---
name: my-new-skill
description: >
  One to two sentences. Describe exactly when Claude should activate this skill
  and what it will do. This is used for skill matching — be specific.
license: MIT
---

# My New Skill Agent

[Full instructions...]
```

### Submitting

1. Fork the repository
2. Create your skill folder using the [template-skill](template-skill/SKILL.md) as a starting point
3. Test your skill across at least: Claude.ai Projects, and either Claude Code or the API
4. Open a pull request with:
   - What domain/use case this skill covers
   - What makes it different from existing skills
   - How you tested it

## Style Guide

- Write instructions for Claude to follow, not for a human to read
- Use imperative language: "Calculate X", "Output Y", "Flag Z"
- Include specific numbers and thresholds — avoid vague words like "high" or "significant"
- Define output format explicitly; show an example when helpful
- Add a disclaimer section for financial, legal, medical, or other regulated domains

## What Will Not Be Accepted

- Duplicate skills that overlap significantly with existing ones
- Skills with no clear output format
- Skills that only restate general Claude capabilities (e.g., "be helpful and detailed")
- Skills with placeholders or incomplete sections
- Skills that require external services the user must separately configure

---

Open issues for suggestions or bug reports.
