package storage

import "gitlab.com/project-together/cpsu-chatbot-api/model"

type AccountStorage interface {
	InsertAccount(username, hashPassword string) error
	FindAccount(username string) (*model.AccountInfo, error)
	UpdateAccountPassword(username, hashPassword string) error
	DeleteAccount(username string) error
}
