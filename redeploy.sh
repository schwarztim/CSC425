set -e

echo "Stopping and removing all Docker containers..."
docker stop $(docker ps -aq) || true
docker rm $(docker ps -aq) || true

echo "Destroying Terraform resources..."
terraform destroy -auto-approve

echo "Initializing Terraform..."
terraform init

echo "Applying Terraform configuration..."
terraform apply -auto-approve

echo "All done!"

