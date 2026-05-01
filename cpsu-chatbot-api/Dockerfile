FROM golang:1.26 AS build

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o /app/cpsu-chatbot-api .

FROM gcr.io/distroless/base-debian10 AS reduce

WORKDIR /

COPY --from=build /app/cpsu-chatbot-api ./

ENTRYPOINT ["./cpsu-chatbot-api", "--mode", "production"]