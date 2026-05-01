package config

import (
	"context"
	"fmt"
	"log"
	"strings"

	"gitlab.com/project-together/cpsu-chatbot-api/internal/environment"

	"github.com/tmc/langchaingo/embeddings"
	"github.com/tmc/langchaingo/llms"
	"github.com/tmc/langchaingo/llms/ollama"
)

func GetLLM(ctx context.Context) (llms.Model, error) {
	provider := strings.ToLower(environment.GetLLMProvider())
	modelName := environment.GetLLMModelName()

	log.Printf("Initializing LLM Provider: %s | Model: %s\n", strings.ToUpper(provider), modelName)

	switch provider {
	case "ollama":
		return ollama.New(
			ollama.WithModel(modelName),
			ollama.WithServerURL(environment.GetOllamaBaseUrl()),
		)
	// case "openai":
	// 	return openai.New(
	// 		openai.WithModel(modelName),
	// 		openai.WithToken(environment.GetOpenAIApiKey()),
	// 	)
	default:
		return nil, fmt.Errorf("unsupported LLM_PROVIDER: %s", provider)
	}
}

func GetEmbedder(ctx context.Context) (embeddings.Embedder, error) {
	provider := strings.ToLower(environment.GetEmbeddingProvider())
	modelName := environment.GetEmbeddingModelName()

	log.Printf("Initializing Embedding Provider: %s | Model: %s\n", strings.ToUpper(provider), modelName)

	switch provider {
	case "ollama":
		llm, err := ollama.New(
			ollama.WithModel(modelName),
			ollama.WithServerURL(environment.GetOllamaBaseUrl()),
		)
		if err != nil {
			return nil, err
		}
		return embeddings.NewEmbedder(llm)
	// case "openai":
	// 	llm, err := openai.New(
	// 		openai.WithModel(modelName),
	// 		openai.WithToken(environment.GetOpenAIApiKey()),
	// 	)
	// 	if err != nil {
	// 		return nil, err
	// 	}
	// 	return embeddings.NewEmbedder(llm)
	default:
		return nil, fmt.Errorf("unsupported EMBEDDING_PROVIDER: %s", provider)
	}
}
