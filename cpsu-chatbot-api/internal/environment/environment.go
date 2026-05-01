package environment

import (
	"log"
	"os"
	"strconv"
)

func mustGetEnv(key string) string {
	value := os.Getenv(key)
	if value == "" {
		log.Fatalf("Environment variable %s is required but not set", key)
	}
	return value
}

func GetRedisHost() string {
	host := os.Getenv("REDIS_HOST")
	if host == "" {
		return "localhost"
	}
	return host
}

func GetRedisPort() string {
	port := os.Getenv("REDIS_PORT")
	if port == "" {
		return "6379"
	}
	return port
}

func GetRedisPassword() string {
	return os.Getenv("REDIS_PASSWORD")
}

func GetRedisDB() int {
	dbStr := os.Getenv("REDIS_DB")
	if dbStr == "" {
		return 0
	}
	db, err := strconv.Atoi(dbStr)
	if err != nil {
		log.Fatalf("Invalid REDIS_DB: %v", err)
	}
	return db
}

func GetJWTSecret() string {
	return mustGetEnv("JWT_SECRET")
}

func GetLLMProvider() string {
	return mustGetEnv("LLM_PROVIDER")
}

func GetLLMModelName() string {
	return mustGetEnv("LLM_MODEL_NAME")
}

func GetEmbeddingProvider() string {
	return mustGetEnv("EMBEDDING_PROVIDER")
}

func GetEmbeddingModelName() string {
	return mustGetEnv("EMBEDDING_MODEL_NAME")
}

func GetVectorDimension() int {
	dimStr := os.Getenv("VECTOR_DIMENSION")
	if dimStr == "" {
		return 1024
	}
	dim, err := strconv.Atoi(dimStr)
	if err != nil {
		log.Fatalf("Invalid VECTOR_DIMENSION: %v", err)
	}
	return dim
}

func GetOllamaBaseUrl() string {
	url := os.Getenv("OLLAMA_BASE_URL")
	if url == "" {
		return "http://localhost:11434"
	}
	return url
}

func GetQdrantHost() string {
	return mustGetEnv("QDRANT_HOST")
}

func GetQdrantPort() int {
	portStr := os.Getenv("QDRANT_PORT")
	if portStr == "" {
		return 6334
	}
	port, err := strconv.Atoi(portStr)
	if err != nil {
		log.Fatalf("Invalid QDRANT_PORT: %v", err)
	}
	return port
}

func GetQdrantApiKey() string {
	return os.Getenv("QDRANT_API_KEY")
}

func GetQdrantUseSSL() bool {
	return mustGetEnv("QDRANT_USE_SSL") == "true"
}

func GetAPIServiceKey() string {
	return mustGetEnv("API_SERVICE_KEY")
}

func GetMinioEndpoint() string {
	return mustGetEnv("MINIO_ENDPOINT")
}

func GetMinioExternalEndpoint() string {
	return mustGetEnv("MINIO_EXTERNAL_ENDPOINT")
}

func GetMinioAccessKey() string {
	return mustGetEnv("MINIO_ACCESS_KEY")
}

func GetMinioSecretKey() string {
	return mustGetEnv("MINIO_SECRET_KEY")
}

func GetMinioBucketName() string {
	return mustGetEnv("MINIO_BUCKET_NAME")
}

func GetMinioUseSSL() string {
	return mustGetEnv("MINIO_USE_SSL")
}

func GetMinioRegion() string {
	return mustGetEnv("MINIO_REGION")
}

func GetAllowOrigins() string {
	return mustGetEnv("VITE_BASE_URL")
}