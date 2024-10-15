#!/bin/bash
set -e

echo "Stopping and force-removing all Docker containers..."
# Forcefully stop and remove all containers, even those not managed by Terraform
docker ps -aq | xargs -r docker stop
docker ps -aq | xargs -r docker rm -f

echo "Killing any lingering processes holding onto port 5432..."
# Find and kill any processes holding onto port 5432 (docker-proxy or others)
sudo lsof -t -i:5432 | xargs -r sudo kill -9

echo "Cleaning up old Docker volumes and networks..."
# Ensure that no containers are using volumes before removing them
docker volume ls -q | grep -v "postgres_data" | xargs -r docker volume rm -f  # Remove all volumes except postgres_data

# Forcefully remove postgres_data volume if it still exists
docker volume rm -f postgres_data || true

# Remove non-default Docker networks
docker network ls --filter "driver=bridge" --format "{{.ID}} {{.Name}}" \
  | grep -v "bridge\|host\|none" \
  | awk '{print $1}' \
  | xargs -r docker network rm || true

echo "Checking if 'postgres_data' volume exists in Terraform state..."
if terraform state show docker_volume.postgres_data >/dev/null 2>&1; then
  echo "Removing 'postgres_data' from Terraform state..."
  terraform state rm docker_volume.postgres_data || true
else
  echo "'postgres_data' not found in Terraform state."
fi

echo "Destroying Terraform resources..."
terraform destroy -auto-approve

echo "Cleaning up old Docker images..."
# Forcefully remove images, including those referenced by stopped containers
docker images -q | xargs -r docker rmi -f  

echo "Cleaning up any leftover Docker resources (prune)..."
docker system prune -af --volumes || true

echo "Initializing Terraform..."
terraform init

echo "Applying Terraform configuration..."
terraform apply -auto-approve

echo "All done!"
