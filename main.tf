terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

# Custom network creation to replace Docker Compose network
resource "docker_network" "csc425_default" {
  name   = "csc425_default"
  driver = "bridge"
}

# Persistent volume creation for PostgreSQL data
resource "docker_volume" "postgres_data" {
  name = "postgres_data"
}

# PostgreSQL image setup
resource "docker_image" "postgres_image" {
  name         = "postgres:latest"
  keep_locally = false
}

# Backend image setup
resource "docker_image" "backend_image" {
  name = "backend:latest"
  build {
    context    = "./backend"
    dockerfile = "./Dockerfile"
    tag        = ["backend:latest"]
  }
  keep_locally = false
}

# Frontend image setup
resource "docker_image" "frontend_image" {
  name = "frontend:latest"
  build {
    context    = "./frontend"
    dockerfile = "./Dockerfile"
    tag        = ["frontend:latest"]
  }
  keep_locally = false
}

# PostgreSQL container setup with correct environment variables
resource "docker_container" "postgres_container" {
  name  = "postgres_container"
  image = docker_image.postgres_image.name

  # Port mapping
  ports {
    internal = 5432
    external = 5432
  }

  # Correct environment variables for PostgreSQL to create the right database and user
  env = [
    "POSTGRES_USER=user",
    "POSTGRES_PASSWORD=password",
    "POSTGRES_DB=hair_salon"
  ]

  # Attach to custom network
  networks_advanced {
    name = docker_network.csc425_default.name
  }

  # Volume mounts for PostgreSQL data and init script
  mounts {
    target = "/var/lib/postgresql/data"
    source = docker_volume.postgres_data.name
    type   = "volume"
  }

  mounts {
    target = "/docker-entrypoint-initdb.d/init.sql"
    source = "${abspath(path.module)}/database/init.sql"
    type   = "bind"
  }

  # Healthcheck to ensure PostgreSQL is ready
  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U user"]
    interval = "30s"
    timeout  = "10s"
    retries  = 5
  }
}

## Backend container setup with correct DATABASE_URL environment variable
resource "docker_container" "backend_container" {
  name  = "backend"
  image = docker_image.backend_image.name

  # Port mapping
  ports {
    internal = 5000
    external = 5000
  }

  # Correct DATABASE_URL environment variable to connect to the "hair_salon" database
  env = [
    "DATABASE_URL=postgresql://user:password@${docker_container.postgres_container.name}:5432/hair_salon"
  ]

  # Attach to custom network
  networks_advanced {
    name = docker_network.csc425_default.name
  }

  # Depends on PostgreSQL being healthy
  depends_on = [docker_container.postgres_container]

  # Healthcheck for backend
  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:5000"]
    interval = "30s"
    timeout  = "10s"
    retries  = 5
  }
}

# Frontend container setup
resource "docker_container" "frontend_container" {
  name  = "frontend_container"
  image = docker_image.frontend_image.name

  # Port mapping
  ports {
    internal = 8000
    external = 8000
  }

  # Environment variables for frontend to connect to backend
  env = [
    "BACKEND_URL=http://backend:5000"
  ]

  # Attach to custom network
  networks_advanced {
    name = docker_network.csc425_default.name
  }

  # Depends on backend being healthy
  depends_on = [docker_container.backend_container]

  # Healthcheck for frontend
  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:8000"]
    interval = "30s"
    timeout  = "10s"
    retries  = 5
  }
}
