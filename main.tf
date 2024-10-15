terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# PostgreSQL image setup
resource "docker_image" "postgres_image" {
  name         = "postgres:latest"
  keep_locally = false
}

# Backend image build from Dockerfile
resource "docker_image" "backend_image" {
  name = "backend:latest"
  build {
    context    = "./backend"
    dockerfile = "./Dockerfile"
    tag        = ["backend:latest"]
  }
  keep_locally = false
}

# Frontend image build from Dockerfile
resource "docker_image" "frontend_image" {
  name = "frontend:latest"
  build {
    context    = "./frontend"
    dockerfile = "./Dockerfile"
    tag        = ["frontend:latest"]
  }
  keep_locally = false
}

# PostgreSQL container setup
resource "docker_container" "postgres_container" {
  name  = "postgres_container"
  image = docker_image.postgres_image.name
  ports {
    internal = 5432
    external = 5432
  }
  env = [
    "POSTGRES_USER=user",
    "POSTGRES_PASSWORD=password",
    "POSTGRES_DB=hair_salon"
  ]

  # Mounts for PostgreSQL data and init.sql
  mounts {
    target = "/var/lib/postgresql/data"
    source = docker_volume.postgres_data.name
    type   = "volume"
  }

  # Bind mount for init.sql
  mounts {
    target = "/docker-entrypoint-initdb.d/init.sql"
    source = pathexpand("${abspath(path.module)}/database/init.sql")
    type   = "bind"
  }
}

# Backend container setup
resource "docker_container" "backend_container" {
  image = docker_image.backend_image.name
  name  = "backend"
  ports {
    internal = 5000
    external = 5000
  }
  env = [
    "DATABASE_URL=postgresql://user:password@${docker_container.postgres_container.name}:5432/hair_salon"
  ]
  depends_on = [docker_container.postgres_container]
}

# Frontend container setup
resource "docker_container" "frontend_container" {
  name  = "frontend_container"
  image = docker_image.frontend_image.name
  ports {
    internal = 8000
    external = 8000
  }
  env = [
    "BACKEND_URL=http://backend:5000"
  ]
  depends_on = [docker_container.backend_container]
}

# Persistent volume creation
resource "docker_volume" "postgres_data" {
  name = "postgres_data"
}
