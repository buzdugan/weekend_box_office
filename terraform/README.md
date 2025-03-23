Commands to run
```shell
# Initialize state file (.tfstate)
terraform init

# Check changes to new infrastructure plan
terraform plan -var="project=<your-gcp-project-id>"

# Create new infrastructure
terraform apply -var="project=<your-gcp-project-id>"

# Delete the infrastructure once you're done to avoid costs on any running services
terraform destroy
```