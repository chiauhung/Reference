# GCP Resource Audit

A lightweight toolkit for auditing GCP infrastructure across environments. I use this to get a full picture of what's running across sandbox, staging, and production — and turn it into a Confluence page for the team.

## Workflow

1. **Export** — Run `get-resources.sh` against each GCP project to dump all resources into JSON files
2. **Analyze** — Run `analyze-resources.py` to get a summary table with created/updated timestamps, exported to CSV
3. **Compare** — Run `compare-environments.py` to build a cross-environment matrix (what exists where, what's sandbox-only and can be cleaned up)
4. **Document** — Paste the CSV output into Confluence as a structured resource inventory page

## Usage

```bash
# Export resources from current gcloud project into a folder
./get-resources.sh sandbox      # or staging / production

# Analyze a single environment
python analyze-resources.py

# Compare across all three environments
python compare-environments.py
```

The comparison script outputs two CSVs:
- `resource_comparison_detailed.csv` — full details per environment
- `resource_comparison_pivot.csv` — simplified X-matrix, good for pasting into Confluence

## What Gets Exported

Cloud Run · Cloud Functions · Pub/Sub · Cloud Scheduler · Memorystore · Dataflow · Artifact Registry · Cloud Build · App Engine · Cloud Storage · Service Accounts · Secrets · VPC · GKE · Vertex AI · Compute Engine

## Stack

`Python` · `gcloud CLI` · `Bash`
