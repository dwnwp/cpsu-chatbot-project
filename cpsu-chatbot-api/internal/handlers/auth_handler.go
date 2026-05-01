package handler

import (
	"fmt"
	"net/http"
	"time"

	"gitlab.com/project-together/cpsu-chatbot-api/internal/environment"
	"gitlab.com/project-together/cpsu-chatbot-api/model"
	"gitlab.com/project-together/cpsu-chatbot-api/storage"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
	"golang.org/x/crypto/bcrypt"
)

type AuthHandler struct {
	AccountStorage storage.AccountStorage
}

func NewAuthHandler(accountStorage storage.AccountStorage) *AuthHandler {
	return &AuthHandler{
		AccountStorage: accountStorage,
	}
}

func (h *AuthHandler) LoginHandler(c echo.Context) error {
	req := new(model.LoginRequest)
	if err := c.Bind(req); err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{
			Message: "invalid request body",
		})
	}


	account, err := h.AccountStorage.FindAccount(req.Username)
	if err != nil {
		fmt.Println("❌ FIND ACCOUNT ERROR:", err)
		return c.JSON(http.StatusUnauthorized, model.MessageResponse{
			Message: "invalid username or password",
		})
	}

	if err := bcrypt.CompareHashAndPassword(
		[]byte(account.Password),
		[]byte(req.Password),
	); err != nil {
		fmt.Println("HASH FROM DB:", account.Password)
		return c.JSON(http.StatusUnauthorized, model.MessageResponse{
			Message: "invalid username or password",
		})
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"sub": req.Username,
		"iat": time.Now().Unix(),
		"exp": time.Now().Add(24 * time.Hour).Unix(),
	})

	tokenString, err := token.SignedString(
		[]byte(environment.GetJWTSecret()),
	)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.MessageResponse{
			Message: "cannot generate token",
		})
	}

	c.SetCookie(&http.Cookie{
		Name:     "access_token",
		Value:    tokenString,
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
		Path:     "/",
		Expires:  time.Now().Add(24 * time.Hour),
	})

	return c.JSON(http.StatusOK, model.MessageResponse{
		Message: "login success",
	})
}

func (h *AuthHandler) RegisterHandler(c echo.Context) error {
	req := new(model.AccountInfo)
	if err := c.Bind(req); err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{
			Message: "invalid request body",
		})
	}

	if req.Username == "" || req.Password == "" {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{
			Message: "all fields are required",
		})
	}

	if _, err := h.AccountStorage.FindAccount(req.Username); err == nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{
			Message: "username already exists",
		})
	}

	hashedPassword, err := bcrypt.GenerateFromPassword(
		[]byte(req.Password),
		bcrypt.DefaultCost,
	)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.MessageResponse{
			Message: "cannot hash password",
		})
	}

	if err := h.AccountStorage.InsertAccount(
		req.Username,
		string(hashedPassword),
	); err != nil {
		return c.JSON(http.StatusInternalServerError, model.MessageResponse{
			Message: "cannot register account",
		})
	}

	return c.JSON(http.StatusCreated, model.MessageResponse{
		Message: "register success",
	})
}

func (h *AuthHandler) DeleteAccountHandler(c echo.Context) error {
	req := new(model.DeleteAccountRequest)
	if err := c.Bind(req); err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{
			Message: "invalid request body",
		})
	}

	if req.Username == "" {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{
			Message: "username is required",
		})
	}

	if err := h.AccountStorage.DeleteAccount(req.Username); err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{
			Message: "account not found",
		})
	}

	return c.JSON(http.StatusCreated, model.MessageResponse{
		Message: "delete account success",
	})
}

func (h *AuthHandler) ResetPasswordHandler(c echo.Context) error {
	req := new(model.ChangePasswordRequest)
	if err := c.Bind(req); err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{
			Message: "invalid request body",
		})
	}

	if req.Username == "" || req.Password == "" || req.NewPassword == "" {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{
			Message: "all fields are required",
		})
	}

	account, err := h.AccountStorage.FindAccount(req.Username)
	if err != nil {
		return c.JSON(http.StatusUnauthorized, model.MessageResponse{
			Message: "invalid username or password",
		})
	}

	if err := bcrypt.CompareHashAndPassword(
		[]byte(account.Password),
		[]byte(req.Password),
	); err != nil {
		return c.JSON(http.StatusUnauthorized, model.MessageResponse{
			Message: "invalid username or password",
		})
	}

	hashedPassword, err := bcrypt.GenerateFromPassword(
		[]byte(req.NewPassword),
		bcrypt.DefaultCost,
	)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.MessageResponse{
			Message: "cannot hash password",
		})
	}

	if err := h.AccountStorage.UpdateAccountPassword(
		req.Username,
		string(hashedPassword),
	); err != nil {
		return c.JSON(http.StatusInternalServerError, model.MessageResponse{
			Message: "cannot update password",
		})
	}

	return c.JSON(http.StatusOK, model.MessageResponse{
		Message: "reset password success",
	})
}

func (h *AuthHandler) LogoutHandler(c echo.Context) error {
	c.SetCookie(&http.Cookie{
		Name:     "access_token",
		Value:    "",
		Path:     "/",
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
		Expires:  time.Now().Add(-1 * time.Hour),
	})

	return c.JSON(http.StatusOK, model.MessageResponse{
		Message: "logout success",
	})
}

func (h *AuthHandler) VerifyHandler(c echo.Context) error {
	return c.JSON(http.StatusOK, model.MessageResponse{Message: "authenticated"})
}
