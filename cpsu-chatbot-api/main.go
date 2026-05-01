package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"sort"

	"gitlab.com/project-together/cpsu-chatbot-api/internal/config"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/connector"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/router"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/environment"

	"github.com/joho/godotenv"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func loadEnv() {
	if err := godotenv.Load("../.env"); err != nil {
		fmt.Println("Error loading .env file.")
	}
}

func getPort(port *string) {
	if *port == "" {
		*port = os.Getenv("PORT_API")
		if *port == "" {
			log.Fatalln("Port is not set. Please set PORT in .env or use -p flag.")
		}
	} else {
		fmt.Println("Using custom port :", *port)
	}
}

func getMode(mode *string) {
	if *mode == "" {
		*mode = "develop"
	} else {
		fmt.Println("Using custom mode:", *mode)
	}
}

func initEcho() *echo.Echo {
	e := echo.New()
	e.Use(middleware.RequestLogger())
	e.Use(middleware.Recover())
	e.Use(middleware.RequestID())
	e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
		AllowOrigins:     []string{"http://localhost:8080", environment.GetAllowOrigins()},
		AllowMethods:     []string{echo.GET, echo.POST, echo.PUT, echo.PATCH, echo.DELETE, echo.OPTIONS},
		AllowCredentials: true,
	}))
	return e
}

func printRoutes(e *echo.Echo) {
	fmt.Println("\nAll registered routes:")
	routes := e.Routes()
	sort.Slice(routes, func(i, j int) bool {
		if routes[i].Path != routes[j].Path {
			return routes[i].Path < routes[j].Path
		}
		return routes[i].Method < routes[j].Method
	})
	for _, route := range routes {
		if route.Method != echo.RouteNotFound {
			fmt.Printf("Method: %s, Path: %s\n", route.Method, route.Path)
		}
	}
}

func startServer(e *echo.Echo, port string) {
	fmt.Println("Starting API on port", port)
	e.Logger.Fatal(e.Start(":" + port))
}

func main() {
	var port, mode string
	flag.StringVar(&port, "p", "", "Port to run the API server on")
	flag.StringVar(&mode, "mode", "", "Mode to run the API server on")
	flag.Parse()
	if mode == "" {
		mode = "develop"
		loadEnv()
	}
	_ = os.Setenv("MODE", mode)
	getPort(&port)
	getMode(&mode)
	e := initEcho()

	// connect
	db := connector.ConnectRedis()
	ctx := context.Background()
	llm, err := config.GetLLM(ctx)
	if err != nil {
		log.Fatalf("Failed to init LLM: %v", err)
	}
	embedder, err := config.GetEmbedder(ctx)
	if err != nil {
		log.Fatalf("Failed to init Embedder: %v", err)
	}
	
	qdrantClient := connector.ConnectQdrant()
	minioClient := connector.ConnectMinio()

	v1 := e.Group("/v1")
	router.InitAuthRouter(v1, db)
	router.InitDocumentRoutes(v1, embedder, llm, qdrantClient, db)
	router.InitImageRouter(v1, minioClient)

	printRoutes(e)

	startServer(e, port)
}
