// AgentOS 2.0 — Knowledge Graph Builder Demo (Go)
// Demonstrates the knowledge-graph-builder skill via the Claude API
// Usage: ANTHROPIC_API_KEY=your_key go run knowledge_graph_demo.go

package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

const (
	anthropicAPIURL = "https://api.anthropic.com/v1/messages"
	defaultModel    = "claude-sonnet-4-6"
	maxTokens       = 4096
)

// Claude API types
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type Request struct {
	Model     string    `json:"model"`
	MaxTokens int       `json:"max_tokens"`
	System    string    `json:"system"`
	Messages  []Message `json:"messages"`
}

type ContentBlock struct {
	Type string `json:"type"`
	Text string `json:"text"`
}

type Usage struct {
	InputTokens  int `json:"input_tokens"`
	OutputTokens int `json:"output_tokens"`
}

type Response struct {
	Content []ContentBlock `json:"content"`
	Usage   Usage          `json:"usage"`
	Error   *struct {
		Message string `json:"message"`
	} `json:"error,omitempty"`
}

// loadSkill reads a SKILL.md file from the repo
func loadSkill(skillName string) (string, error) {
	exePath, err := os.Executable()
	if err != nil {
		return "", err
	}
	repoRoot := filepath.Dir(filepath.Dir(exePath))
	skillPath := filepath.Join(repoRoot, skillName, "SKILL.md")

	// Fallback: look relative to source file location
	if _, err := os.Stat(skillPath); os.IsNotExist(err) {
		skillPath = filepath.Join("..", skillName, "SKILL.md")
	}

	data, err := os.ReadFile(skillPath)
	if err != nil {
		return "", fmt.Errorf("skill %q not found: %w", skillName, err)
	}
	return string(data), nil
}

// callClaude sends a request to the Claude API
func callClaude(apiKey, system, question string) (*Response, error) {
	reqBody := Request{
		Model:     defaultModel,
		MaxTokens: maxTokens,
		System:    system,
		Messages:  []Message{{Role: "user", Content: question}},
	}

	payload, err := json.Marshal(reqBody)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest("POST", anthropicAPIURL, bytes.NewReader(payload))
	if err != nil {
		return nil, err
	}

	req.Header.Set("x-api-key", apiKey)
	req.Header.Set("anthropic-version", "2023-06-01")
	req.Header.Set("content-type", "application/json")

	httpClient := &http.Client{Timeout: 120 * time.Second}
	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var claudeResp Response
	if err := json.Unmarshal(body, &claudeResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	if claudeResp.Error != nil {
		return nil, fmt.Errorf("API error: %s", claudeResp.Error.Message)
	}

	return &claudeResp, nil
}

func runKnowledgeGraphDemo(apiKey string) error {
	fmt.Println("=== AgentOS: KnowledgeGraphBuilder Demo ===\n")

	skill, err := loadSkill("knowledge-graph-builder")
	if err != nil {
		return fmt.Errorf("could not load skill: %w", err)
	}

	question := `Design a knowledge graph schema for an AI company ecosystem.
Entities: Companies, People, Technologies, Products, Funding Rounds.
Include: entity types with properties, relationship types with cardinality,
sample Cypher CREATE statements, and 3 example multi-hop query patterns.
Also recommend whether to use GraphRAG or vector RAG for this use case.`

	fmt.Println("Question:", question)
	fmt.Println(separator())

	start := time.Now()
	resp, err := callClaude(apiKey, skill, question)
	if err != nil {
		return err
	}

	elapsed := time.Since(start)
	fmt.Printf("\n[KnowledgeGraph] (%d tokens in %dms)\n\n",
		resp.Usage.InputTokens+resp.Usage.OutputTokens,
		elapsed.Milliseconds())
	fmt.Println(resp.Content[0].Text)
	fmt.Println(separator())

	return nil
}

func separator() string {
	return "────────────────────────────────────────────────────"
}

func main() {
	apiKey := os.Getenv("ANTHROPIC_API_KEY")

	fmt.Printf("AgentOS 2.0 — KnowledgeGraph Builder\n")
	fmt.Printf("Model: %s\n\n", defaultModel)

	if apiKey == "" {
		fmt.Println("Set ANTHROPIC_API_KEY to run the demo.")
		fmt.Println("  export ANTHROPIC_API_KEY=your_key")
		fmt.Println("  go run knowledge_graph_demo.go")
		os.Exit(0)
	}

	if err := runKnowledgeGraphDemo(apiKey); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
