package connector

import (
	"context"
	"fmt"
	"log"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/environment"
)

func ConnectMinio() *minio.Client {
	endpoint := environment.GetMinioEndpoint()
	accessKeyID := environment.GetMinioAccessKey()
	secretAccessKey := environment.GetMinioSecretKey()
	useSSL := environment.GetMinioUseSSL() == "true"
	region := environment.GetMinioRegion()

	minioClient, err := minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKeyID, secretAccessKey, ""),
		Secure: useSSL,
		Region: region,
	})
	if err != nil {
		log.Fatalf("Cannot connect to MinIO: %v", err)
	}
	bucketName := environment.GetMinioBucketName()
	policy := fmt.Sprintf(`{"Version": "2012-10-17","Statement": [{"Sid": "PublicReadOnly","Effect": "Allow","Principal": {"AWS": ["*"]},"Action": ["s3:GetObject","s3:GetObjectVersion"],"Resource": ["arn:aws:s3:::%s/*"]},{"Sid": "PublicListBucket","Effect": "Allow","Principal": {"AWS": ["*"]},"Action": ["s3:ListBucket","s3:GetBucketLocation"],"Resource": ["arn:aws:s3:::%s"]}]}`, bucketName, bucketName)
	err = minioClient.SetBucketPolicy(context.Background(), bucketName, policy)
	if err != nil {
		log.Fatalf("Cannot set bucket policy: %v", err)
	}

	log.Println("MinIO connected")
	return minioClient
}
