# Docker Instructions for Home Management System

This guide will help you build and run the Home Management System application using Docker.

## Prerequisites

- Docker installed on your system ([Download Docker](https://www.docker.com/get-started))
- Docker Compose (optional, for multi-container setup)
- PostgreSQL database (can be run in a separate container or use a cloud service)

## Quick Start

### Option 1: Build and Run with Docker (Manual)

#### 1. Build the Docker Image

```bash
docker build -t home-management-system .
```

#### 2. Run the Container

**With environment variables:**

```bash
docker run -d \
  --name home-management \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/dbname" \
  -e SECRET_KEY="your-secret-key-here" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  home-management-system
```

**With .env file:**

```bash
docker run -d \
  --name home-management \
  -p 8000:8000 \
  --env-file .env \
  home-management-system
```

#### 3. Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

### Option 2: Using Docker Compose (Recommended)

Create a `docker-compose.yml` file in your project root:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: homeuser
      POSTGRES_PASSWORD: homepass
      POSTGRES_DB: homemanagement
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U homeuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://homeuser:homepass@db:5432/homemanagement
      SECRET_KEY: your-secret-key-change-this-in-production
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./templates:/app/templates
      - ./static:/app/static

volumes:
  postgres_data:
```

#### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT Configuration
SECRET_KEY=your-very-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Docker Commands Reference

### Building

```bash
# Build the image
docker build -t home-management-system .

# Build with no cache
docker build --no-cache -t home-management-system .

# Build with a specific tag
docker build -t home-management-system:v1.0.0 .
```

### Running

```bash
# Run in detached mode
docker run -d -p 8000:8000 --name home-management home-management-system

# Run with interactive terminal
docker run -it -p 8000:8000 --name home-management home-management-system

# Run with volume mounts for development
docker run -d -p 8000:8000 \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/templates:/app/templates \
  -v $(pwd)/static:/app/static \
  --name home-management \
  home-management-system
```

### Managing Containers

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Stop a container
docker stop home-management

# Start a stopped container
docker start home-management

# Restart a container
docker restart home-management

# Remove a container
docker rm home-management

# Remove a running container (force)
docker rm -f home-management

# View container logs
docker logs home-management

# Follow container logs
docker logs -f home-management

# Execute commands in running container
docker exec -it home-management bash
```

### Managing Images

```bash
# List images
docker images

# Remove an image
docker rmi home-management-system

# Remove all unused images
docker image prune

# Remove all images
docker image prune -a
```

## Connecting to External Database

If you're using a cloud PostgreSQL service (Railway, Supabase, etc.):

```bash
docker run -d \
  --name home-management \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@your-cloud-host:port/dbname?sslmode=require" \
  -e SECRET_KEY="your-secret-key" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  home-management-system
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs home-management

# Check if port is already in use
docker ps -a | grep 8000
```

### Database connection issues

```bash
# Verify database is accessible
docker exec -it home-management python -c "from src.database import database; import asyncio; asyncio.run(database.connect())"

# Check environment variables
docker exec -it home-management env | grep DATABASE_URL
```

### Permission issues

```bash
# Run with specific user
docker run -d -p 8000:8000 --user $(id -u):$(id -g) home-management-system
```

## Production Deployment

For production deployments, consider:

1. **Use multi-stage builds** to reduce image size
2. **Don't expose PostgreSQL port** publicly
3. **Use Docker secrets** for sensitive data
4. **Set up proper logging** with volume mounts
5. **Use health checks** for container orchestration
6. **Implement backup strategies** for database volumes
7. **Use reverse proxy** (nginx) for SSL/TLS termination

### Example Production Dockerfile

```dockerfile
FROM python:3.12-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 appuser

WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app/src

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Docker Hub Publishing

```bash
# Tag your image
docker tag home-management-system yourusername/home-management-system:latest

# Login to Docker Hub
docker login

# Push to Docker Hub
docker push yourusername/home-management-system:latest
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Docker Documentation](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)

---

**Note**: Always change default passwords and secret keys in production environments!
