package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
)

// BenchmarkSchema represents the root of the tasks.json file.
type BenchmarkSchema struct {
	Tasks []Task `json:"tasks"`
}

// Task represents a single evaluation scenario.
type Task struct {
	TaskID     string     `json:"task_id"`
	Repository Repository `json:"repository"`
	Evaluation Evaluation `json:"evaluation"`
	Metadata   Metadata   `json:"metadata"`
}

// Repository describes the target codebase for the task.
type Repository struct {
	URL      string `json:"url"`
	Commit   string `json:"commit"`
	Language string `json:"language"`
}

// Evaluation contains the ground truth and prompt for measuring AI performance.
type Evaluation struct {
	UserPrompt         string             `json:"user_prompt"`
	GroundTruthContext GroundTruthContext `json:"ground_truth_context"`
	GroundTruthPatch   string             `json:"ground_truth_patch"`
	Verification       Verification       `json:"verification"`
}

// GroundTruthContext defines exactly what the AI should have retrieved.
type GroundTruthContext struct {
	RequiredFiles   []string `json:"required_files"`
	RequiredSymbols []string `json:"required_symbols"`
}

// Verification defines how to test the AI's generated patch.
type Verification struct {
	SetupCommand string `json:"setup_command"`
	TestCommand  string `json:"test_command"`
}

// Metadata contains classification info for the task.
type Metadata struct {
	Difficulty string   `json:"difficulty"`
	Category   string   `json:"category"`
	Tags       []string `json:"tags"`
}

func main() {
	fmt.Println("Foldwork Benchmark Evaluator v0.1.0")

	// 1. Load tasks.json
	// TODO: Make this configurable via CLI flag
	taskFile := "test/benchmark/tasks.json"
	data, err := os.ReadFile(taskFile)
	if err != nil {
		log.Fatalf("Failed to read tasks file: %v", err)
	}

	var schema BenchmarkSchema
	if err := json.Unmarshal(data, &schema); err != nil {
		log.Fatalf("Failed to parse tasks schema: %v", err)
	}

	fmt.Printf("Loaded %d tasks from benchmark suite.\n", len(schema.Tasks))

	// 2. Iterate through tasks and evaluate
	for _, task := range schema.Tasks {
		evaluateTask(task)
	}
}

// evaluateTask coordinates the evaluation of a single task.
func evaluateTask(task Task) {
	fmt.Printf("\n--- Evaluating Task: %s ---\n", task.TaskID)
	fmt.Printf("Prompt: %s\n", task.Evaluation.UserPrompt)

	// Step 1: Clone/checkout repository (Mocked for now)
	fmt.Printf("Checking out %s @ %s...\n", task.Repository.URL, task.Repository.Commit)

	// Step 2: Spin up local LLM agent to simulate retrieval
	agent := NewAgent("qwen2.5-coder:7b") // Defaulting to Qwen for coding tasks
	retrievedSymbols, err := agent.RunSimulatedRetrieval(task.Evaluation.UserPrompt)
	if err != nil {
		fmt.Printf("[Error] Agent failed: %v\n", err)
		return
	}

	// Step 3: Calculate Context Precision
	precision := calculateContextPrecision(task.Evaluation.GroundTruthContext.RequiredSymbols, retrievedSymbols)
	fmt.Printf("Context Precision: %.2f%%\n", precision*100)
}

// calculateContextPrecision computes the ratio of useful symbols to total retrieved/missing symbols.
func calculateContextPrecision(required []string, retrieved []string) float64 {
	requiredMap := make(map[string]bool)
	for _, sym := range required {
		requiredMap[sym] = true
	}

	retrievedMap := make(map[string]bool)
	for _, sym := range retrieved {
		retrievedMap[sym] = true
	}

	var truePositives int
	var falsePositives int

	for sym := range retrievedMap {
		if requiredMap[sym] {
			truePositives++
		} else {
			falsePositives++
		}
	}

	var falseNegatives int
	for sym := range requiredMap {
		if !retrievedMap[sym] {
			falseNegatives++
		}
	}

	totalDenominator := truePositives + falsePositives + falseNegatives
	if totalDenominator == 0 {
		return 0.0
	}

	return float64(truePositives) / float64(totalDenominator)
}
