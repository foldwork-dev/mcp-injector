package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

// OllamaChatRequest represents the request body for Ollama's /api/chat endpoint.
type OllamaChatRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
	Stream   bool      `json:"stream"`
	Tools    []Tool    `json:"tools,omitempty"`
}

type Message struct {
	Role    string     `json:"role"`
	Content string     `json:"content"`
	ToolCalls []ToolCall `json:"tool_calls,omitempty"`
}

type Tool struct {
	Type     string       `json:"type"`
	Function ToolFunction `json:"function"`
}

type ToolFunction struct {
	Name        string         `json:"name"`
	Description string         `json:"description"`
	Parameters  ToolParameters `json:"parameters"`
}

type ToolParameters struct {
	Type       string              `json:"type"`
	Properties map[string]Property `json:"properties"`
	Required   []string            `json:"required"`
}

type Property struct {
	Type        string `json:"type"`
	Description string `json:"description"`
}

type ToolCall struct {
	Function ToolCallFunction `json:"function"`
}

type ToolCallFunction struct {
	Name      string `json:"name"`
	Arguments map[string]interface{} `json:"arguments"`
}

// OllamaChatResponse represents the response from Ollama.
type OllamaChatResponse struct {
	Message Message `json:"message"`
}

// Agent represents the local LLM agent runner.
type Agent struct {
	Endpoint string
	Model    string
}

// NewAgent creates a new Ollama agent instance.
func NewAgent(model string) *Agent {
	return &Agent{
		Endpoint: "http://localhost:11434/api/chat",
		Model:    model,
	}
}

// RunSimulatedRetrieval connects to Ollama, provides the injector_retrieve tool,
// and returns the list of symbols the AI decided to retrieve.
func (a *Agent) RunSimulatedRetrieval(prompt string) ([]string, error) {
	fmt.Printf("[Agent] Sending prompt to local model (%s)...\n", a.Model)

	reqBody := OllamaChatRequest{
		Model:  a.Model,
		Stream: false,
		Messages: []Message{
			{
				Role:    "system",
				Content: "You are an autonomous AI coding agent. You must use the provided tools to retrieve exactly the files and functions needed to solve the user's task. Do not explain yourself, just call the tools.",
			},
			{
				Role:    "user",
				Content: prompt,
			},
		},
		Tools: []Tool{
			{
				Type: "function",
				Function: ToolFunction{
					Name:        "injector_retrieve",
					Description: "Retrieves the exact code for a specific symbol or file to help solve the task.",
					Parameters: ToolParameters{
						Type: "object",
						Properties: map[string]Property{
							"symbol": {
								Type:        "string",
								Description: "The name of the function or file you need to read (e.g. 'GenerateToken').",
							},
						},
						Required: []string{"symbol"},
					},
				},
			},
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %v", err)
	}

	resp, err := http.Post(a.Endpoint, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to reach Ollama at %s: %v. Is Ollama running?", a.Endpoint, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("ollama returned status %d: %s", resp.StatusCode, string(bodyBytes))
	}

	var chatResp OllamaChatResponse
	if err := json.NewDecoder(resp.Body).Decode(&chatResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %v", err)
	}

	var retrievedSymbols []string
	if len(chatResp.Message.ToolCalls) > 0 {
		for _, toolCall := range chatResp.Message.ToolCalls {
			if toolCall.Function.Name == "injector_retrieve" {
				if sym, ok := toolCall.Function.Arguments["symbol"].(string); ok {
					retrievedSymbols = append(retrievedSymbols, sym)
					fmt.Printf("[Agent] Model decided to retrieve symbol: %s\n", sym)
				}
			}
		}
	} else {
		fmt.Printf("[Agent] Model did not call any tools. It responded: %s\n", chatResp.Message.Content)
	}

	return retrievedSymbols, nil
}
