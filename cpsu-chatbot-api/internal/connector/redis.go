package connector

import (
	"context"
	"fmt"
	"log"

	"gitlab.com/project-together/cpsu-chatbot-api/internal/environment"

	"github.com/redis/go-redis/v9"
)

func ConnectRedis() *redis.Client {
	ctx := context.Background()

	host := environment.GetRedisHost()
	port := environment.GetRedisPort()
	password := environment.GetRedisPassword()
	dbNum := environment.GetRedisDB()

	addr := fmt.Sprintf("%s:%s", host, port)

	client := redis.NewClient(&redis.Options{
		Addr:     addr,
		Password: password,
		DB:       dbNum,
	})

	if err := client.Ping(ctx).Err(); err != nil {
		log.Fatal("Redis connection error:", err)
	}

	log.Println("Redis connected")

	return client
}
