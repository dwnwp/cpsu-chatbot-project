package storage

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"gitlab.com/project-together/cpsu-chatbot-api/model"

	"github.com/redis/go-redis/v9"
)

type accountStorage struct {
	Client *redis.Client
}

func NewAccountStorage(client *redis.Client) AccountStorage {
	return &accountStorage{
		Client: client,
	}
}

func accountKey(username string) string {
	return fmt.Sprintf("account:%s", username)
}

func (as *accountStorage) InsertAccount(username, hashPassword string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	account := model.AccountInfo{
		Username:  username,
		Password:  hashPassword,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	data, err := json.Marshal(account)
	if err != nil {
		return err
	}

	return as.Client.Set(ctx, accountKey(username), data, 0).Err()
}

func (as *accountStorage) FindAccount(username string) (*model.AccountInfo, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	val, err := as.Client.Get(ctx, accountKey(username)).Result()
	if err == redis.Nil {
		return nil, fmt.Errorf("account not found")
	} else if err != nil {
		return nil, err
	}

	var account model.AccountInfo
	if err := json.Unmarshal([]byte(val), &account); err != nil {
		return nil, err
	}

	fmt.Println("FOUND ACCOUNT:", account)
	return &account, nil
}

func (as *accountStorage) UpdateAccountPassword(username, hashPassword string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	account, err := as.FindAccount(username)
	if err != nil {
		return err
	}

	account.Password = hashPassword
	account.UpdatedAt = time.Now()

	data, err := json.Marshal(account)
	if err != nil {
		return err
	}

	return as.Client.Set(ctx, accountKey(username), data, 0).Err()
}

func (as *accountStorage) DeleteAccount(username string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	deletedCount, err := as.Client.Del(ctx, accountKey(username)).Result()
	if err != nil {
		return err
	}
	if deletedCount == 0 {
		return fmt.Errorf("account not found")
	}
	return nil
}
