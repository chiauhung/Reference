#!/bin/bash

PROJECT=$(gcloud config get-value project 2>/dev/null)
FOLDER=${1:-sandbox}
REGION=asia-southeast1

echo "===================================="
echo "Exporting GCP resources from project: $PROJECT"
echo "Target folder: $FOLDER"
echo "Region: $REGION"
echo "===================================="
echo ""

# Create folder if it doesn't exist
mkdir -p $FOLDER

echo "Exporting API Gateway..."
gcloud api-gateway gateways list --format=json > $FOLDER/api_gateway.json 2>/dev/null || echo "[]" > $FOLDER/api_gateway.json

echo "Exporting App Engine..."
gcloud app services list --format=json > $FOLDER/app_engine_services.json 2>/dev/null || echo "[]" > $FOLDER/app_engine_services.json
gcloud app versions list --format=json > $FOLDER/app_engine_versions.json 2>/dev/null || echo "[]" > $FOLDER/app_engine_versions.json

echo "Exporting Artifact Registry..."
gcloud artifacts repositories list --format=json > $FOLDER/artifact_repos.json 2>/dev/null || echo "[]" > $FOLDER/artifact_repos.json

echo "Exporting Cloud Build..."
gcloud builds triggers list --format=json > $FOLDER/cloud_build_triggers.json 2>/dev/null || echo "[]" > $FOLDER/cloud_build_triggers.json

echo "Exporting Dataflow..."
gcloud dataflow jobs list --format=json --region=$REGION > $FOLDER/dataflow_jobs.json 2>/dev/null || echo "[]" > $FOLDER/dataflow_jobs.json


echo "Exporting Memorystore..."
gcloud redis instances list --region=$REGION --format=json > $FOLDER/memorystore.json 2>/dev/null || echo "[]" > $FOLDER/memorystore.json

echo "Exporting Pub/Sub..."
gcloud pubsub topics list --format=json > $FOLDER/pubsub_topics.json 2>/dev/null || echo "[]" > $FOLDER/pubsub_topics.json
gcloud pubsub subscriptions list --format=json > $FOLDER/pubsub_subs.json 2>/dev/null || echo "[]" > $FOLDER/pubsub_subs.json

echo "Exporting Cloud Run..."
gcloud run services list --platform=managed --format=json --region=$REGION > $FOLDER/cloud_run_services.json 2>/dev/null || echo "[]" > $FOLDER/cloud_run_services.json

echo "Exporting Cloud Functions..."
gcloud functions list --format=json > $FOLDER/cloud_functions.json 2>/dev/null || echo "[]" > $FOLDER/cloud_functions.json

echo "Exporting Scheduler..."
gcloud scheduler jobs list --location=$REGION --format=json > $FOLDER/scheduler.json 2>/dev/null || echo "[]" > $FOLDER/scheduler.json

echo "Exporting Storage..."
gcloud storage buckets list --format=json > $FOLDER/buckets.json 2>/dev/null || echo "[]" > $FOLDER/buckets.json

echo "Exporting Service Accounts..."
gcloud iam service-accounts list --format=json > $FOLDER/service_accounts.json 2>/dev/null || echo "[]" > $FOLDER/service_accounts.json

echo "Exporting Secrets..."
gcloud secrets list --format=json > $FOLDER/secrets.json 2>/dev/null || echo "[]" > $FOLDER/secrets.json

echo "Exporting Workflows..."
gcloud workflows list --format=json > $FOLDER/workflows.json 2>/dev/null || echo "[]" > $FOLDER/workflows.json

echo "Exporting Vertex AI Endpoints..."
gcloud ai endpoints list --region=$REGION --format=json > $FOLDER/vertex_ai_endpoints.json 2>/dev/null || echo "[]" > $FOLDER/vertex_ai_endpoints.json

echo "Exporting Vertex AI Models..."
gcloud ai models list --region=$REGION --format=json > $FOLDER/vertex_ai_models.json 2>/dev/null || echo "[]" > $FOLDER/vertex_ai_models.json

echo "Exporting Vertex AI Datasets..."
gcloud ai datasets list --region=$REGION --format=json > $FOLDER/vertex_ai_datasets.json 2>/dev/null || echo "[]" > $FOLDER/vertex_ai_datasets.json

echo "Exporting VPC Networks..."
gcloud compute networks list --format=json > $FOLDER/vpc_networks.json 2>/dev/null || echo "[]" > $FOLDER/vpc_networks.json

echo "Exporting VPC Subnets..."
gcloud compute networks subnets list --format=json > $FOLDER/vpc_subnets.json 2>/dev/null || echo "[]" > $FOLDER/vpc_subnets.json

echo "Exporting Firewall Rules..."
gcloud compute firewall-rules list --format=json > $FOLDER/firewall_rules.json 2>/dev/null || echo "[]" > $FOLDER/firewall_rules.json

echo "Exporting GKE Clusters..."
gcloud container clusters list --format=json > $FOLDER/gke_clusters.json 2>/dev/null || echo "[]" > $FOLDER/gke_clusters.json

echo "Exporting Dataplex Lakes..."
gcloud dataplex lakes list --location=$REGION --format=json > $FOLDER/dataplex_lakes.json 2>/dev/null || echo "[]" > $FOLDER/dataplex_lakes.json

echo "Exporting Data Catalog Entries..."
gcloud data-catalog entries list --format=json > $FOLDER/data_catalog_entries.json 2>/dev/null || echo "[]" > $FOLDER/data_catalog_entries.json

echo "Exporting Compute Engine Instances..."
gcloud compute instances list --format=json > $FOLDER/compute_instances.json 2>/dev/null || echo "[]" > $FOLDER/compute_instances.json

echo "Exporting Compute Engine Disks..."
gcloud compute disks list --format=json > $FOLDER/compute_disks.json 2>/dev/null || echo "[]" > $FOLDER/compute_disks.json



echo ""
echo "===================================="
echo "Export complete! Files saved to: $FOLDER/"
echo "===================================="



# echo "Exporting DocumentAI..."
# # Try different command formats for DocumentAI
# gcloud ai document-ai processors list --location=$REGION --format=json > $FOLDER/documentai_processors.json 2>/dev/null || \
# gcloud alpha document-ai processors list --location=$REGION --format=json > $FOLDER/documentai_processors.json 2>/dev/null || \
# echo "[]" > $FOLDER/documentai_processors.json

# echo "Exporting Vertex AI Search Datastores..."
# gcloud alpha discovery-engine data-stores list --location=$REGION --format=json > $FOLDER/vertex_ai_search_datastores.json 2>/dev/null || \
# gcloud discovery-engine data-stores list --location=$REGION --format=json > $FOLDER/vertex_ai_search_datastores.json 2>/dev/null || \
# echo "[]" > $FOLDER/vertex_ai_search_datastores.json

# echo "Exporting SQL..."
# gcloud sql instances list --format=json > $FOLDER/sql_instances.json 2>/dev/null || echo "[]" > $FOLDER/sql_instances.json

# echo "Exporting Notebooks (Vertex AI Workbench)..."
# gcloud notebooks instances list --location=$REGION --format=json > $FOLDER/notebooks_instances.json 2>/dev/null || \
# gcloud workbench instances list --location=$REGION --format=json > $FOLDER/notebooks_instances.json 2>/dev/null || \
# echo "[]" > $FOLDER/notebooks_instances.json