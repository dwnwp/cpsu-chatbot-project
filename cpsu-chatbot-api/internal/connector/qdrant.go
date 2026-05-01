package connector

import (
	"log"

	"github.com/qdrant/go-client/qdrant"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/environment"
)

func ConnectQdrant() *qdrant.Client {
	config := qdrant.Config{
		Host:   environment.GetQdrantHost(),
		Port:   environment.GetQdrantPort(),
		UseTLS: environment.GetQdrantUseSSL(),
	}

	apiKey := environment.GetQdrantApiKey()
	if apiKey != "" {
		config.APIKey = apiKey
	}

	qdrantClient, err := qdrant.NewClient(&config)
	if err != nil {
		log.Fatalf("Failed to create Qdrant client: %v", err)
	}

	log.Println("Qdrant connected")

	return qdrantClient
}
