package router

import (
	"log"
	"net/http"

	"gitlab.com/project-together/cpsu-chatbot-api/internal/environment"
	handler "gitlab.com/project-together/cpsu-chatbot-api/internal/handlers"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/middleware"
	"gitlab.com/project-together/cpsu-chatbot-api/model"
	"gitlab.com/project-together/cpsu-chatbot-api/storage"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
)

func InitAuthRouter(e *echo.Group, db *redis.Client) {
	accountStorage := storage.NewAccountStorage(db)
	authHandler := handler.NewAuthHandler(accountStorage)

	authGroup := e.Group(
		"/auth",
		middleware.RateLimiter(middleware.NewRateLimiterMemoryStore(10)),
	)
	authGroup.POST("/login", authHandler.LoginHandler)
	authGroup.POST("/password-reset", authHandler.ResetPasswordHandler)
	authGroup.POST("/logout", authHandler.LogoutHandler, authMiddleware)
	authGroup.GET("/verify", authHandler.VerifyHandler, authMiddleware)

	e.POST("/accounts", authHandler.RegisterHandler, apiKeyMiddleware)
	e.DELETE("/accounts", authHandler.DeleteAccountHandler, apiKeyMiddleware)
}

func apiKeyMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		apiKey := c.Request().Header.Get("x-api-key")
		expectedKey := environment.GetAPIServiceKey()
		if apiKey != expectedKey {
			return echo.NewHTTPError(http.StatusUnauthorized, "invalid or missing API key")
		}
		return next(c)
	}
}

func authMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		cookie, err := c.Cookie("access_token")
		if err != nil {
			log.Println(err)
			return c.JSON(http.StatusUnauthorized, model.MessageResponse{Message: "missing token"})
		}

		jwtSecret := environment.GetJWTSecret()
		token, err := jwt.Parse(cookie.Value, func(t *jwt.Token) (any, error) {
			return []byte(jwtSecret), nil
		})
		if err != nil || !token.Valid {
			log.Println(err)
			return c.JSON(http.StatusUnauthorized, model.MessageResponse{Message: "invalid token"})
		}

		return next(c)
	}
}
