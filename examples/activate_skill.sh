#!/usr/bin/env bash
# AgentOS 2.0 — Shell skill activator
# Activate any SKILL.md via the Claude API using curl
# Usage: ./activate_skill.sh <skill-name> "<your question>"
# Example: ./activate_skill.sh quant-trader "Give me a NVDA trade signal"

set -euo pipefail

SKILL_NAME="${1:-}"
QUESTION="${2:-}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="${ANTHROPIC_MODEL:-claude-sonnet-4-6}"
MAX_TOKENS="${ANTHROPIC_MAX_TOKENS:-8096}"

# ── Validation ─────────────────────────────────────────────────────────────
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "Error: ANTHROPIC_API_KEY environment variable not set." >&2
  echo "  export ANTHROPIC_API_KEY=your_key_here" >&2
  exit 1
fi

if [[ -z "$SKILL_NAME" ]]; then
  echo "Usage: $0 <skill-name> \"<question>\"" >&2
  echo ""
  echo "Available skills:"
  find "$REPO_ROOT" -maxdepth 2 -name "SKILL.md" \
    | sed "s|$REPO_ROOT/||" | sed 's|/SKILL.md||' | sort | column
  exit 1
fi

SKILL_FILE="$REPO_ROOT/$SKILL_NAME/SKILL.md"
if [[ ! -f "$SKILL_FILE" ]]; then
  echo "Error: Skill '$SKILL_NAME' not found at $SKILL_FILE" >&2
  exit 1
fi

if [[ -z "$QUESTION" ]]; then
  echo "Error: Question cannot be empty." >&2
  echo "  Usage: $0 $SKILL_NAME \"Your question here\"" >&2
  exit 1
fi

# ── Load skill ──────────────────────────────────────────────────────────────
SKILL_CONTENT="$(cat "$SKILL_FILE")"
echo "✦ Activating skill: $SKILL_NAME"
echo "✦ Model: $MODEL"
echo "✦ Question: $QUESTION"
echo "─────────────────────────────────────────────────────"

# ── Build JSON payload ──────────────────────────────────────────────────────
PAYLOAD="$(jq -n \
  --arg model "$MODEL" \
  --argjson max_tokens "$MAX_TOKENS" \
  --arg system "$SKILL_CONTENT" \
  --arg question "$QUESTION" \
  '{
    model: $model,
    max_tokens: $max_tokens,
    system: $system,
    messages: [{ role: "user", content: $question }]
  }')"

# ── Call Claude API ─────────────────────────────────────────────────────────
RESPONSE="$(curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d "$PAYLOAD")"

# ── Extract and print response ──────────────────────────────────────────────
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
  echo "API Error:" >&2
  echo "$RESPONSE" | jq '.error' >&2
  exit 1
fi

echo ""
echo "$RESPONSE" | jq -r '.content[0].text'
echo ""
echo "─────────────────────────────────────────────────────"
INPUT_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.input_tokens')
OUTPUT_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.output_tokens')
echo "Tokens: ${INPUT_TOKENS} in / ${OUTPUT_TOKENS} out"
