<div align="center">

# CPSU Chatbot Project

_A full-stack, AI-powered chatbot system with Retrieval-Augmented Generation (RAG)_

</div>

A comprehensive chatbot application featuring a modern web interface, a robust backend API, and an AI-powered webhook. It utilizes a microservices architecture to deliver scalable and intelligent conversational experiences.

## Features

- **AI-Powered Responses** - Integrates LangChain, LangGraph, and Ollama for advanced RAG workflows.
- **Semantic Caching** - Utilizes Redis for semantic caching to accelerate responses and reduce LLM load.
- **Vector Search** - Employs Qdrant for fast and accurate similarity searches across document embeddings.
- **Microservices Architecture** - Separated concerns with dedicated Frontend, API, and Webhook services.
- **Message Queueing** - Uses RabbitMQ for robust asynchronous task processing.
- **Object Storage** - Integrated with MinIO for scalable file and document management.
- **Unified Gateway** - Nginx reverse proxy for path-based routing and seamless service access.

## Architecture

The project is divided into three main application services and several infrastructure components:

- **Frontend (`cpsu-chatbot-frontend`)**: A modern SPA built with Vue 3, Vite, Tailwind CSS, and Pinia.
- **API (`cpsu-chatbot-api`)**: A robust backend service written in Go to handle core business logic and data management.
- **Webhook (`cpsu-chatbot-webhook`)**: A Python/FastAPI service powering the conversational AI using LangChain and LINE Messaging API integrations and Facebook Messenger API integrations.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/dwnwp/cpsu-chatbot-project.git
   cd cpsu-chatbot-project
   ```

2. Configure environment variables:
   Create a `.env` file in the root directory and populate it with the necessary configuration for all services. Refer to the individual service directories for specific environment variable requirements.

## Usage

Start the entire application stack using Docker Compose:

```bash
docker-compose up -d --build
```

> [!NOTE]
> The initial build may take some time as it pulls images for Redis, MinIO, Qdrant, RabbitMQ, and builds the custom application containers.

Once the containers are running, the services will be accessible via the Nginx reverse proxy according to your configured ports.

### Stopping the services

To stop and remove the containers:

```bash
docker-compose down
```

> [!WARNING]  
> If you wish to remove the persistent data volumes (database, storage, caches), append the `-v` flag: `docker-compose down -v`. This action is irreversible.

## Project Structure

```text
.
├── cpsu-chatbot-frontend/  # Vue 3 UI
├── cpsu-chatbot-api/       # Go Backend API
├── cpsu-chatbot-webhook/   # Python AI Webhook
├── docker_volumes/         # Persistent data storage for infra
├── nginx/                  # Reverse proxy configuration
└── docker-compose.yml      # Multi-container orchestration
```
