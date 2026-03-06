#!/usr/bin/env python3
"""
GCP Resource Environment Comparison
Compares resources across sandbox, staging, and production environments.
Creates a matrix showing which resources exist in which environment.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def normalize_resource_name(name: str, resource_type: str) -> str:
    """
    Normalize resource names by removing environment-specific prefixes/suffixes.
    This allows matching the same logical resource across different environments.
    """
    # Convert to lowercase for comparison
    normalized = name.lower()

    # Special handling for Dataflow jobs - remove timestamp and region suffix
    # Pattern: my-dataflow-job-20250711-025411-sg -> my-dataflow-job
    if resource_type == 'Dataflow Job':
        # Remove timestamp pattern: -YYYYMMDD-HHMMSS
        normalized = re.sub(r'-\d{8}-\d{6}', '', normalized)
        # Remove region suffix: -sg, -de, -eu, -us, -asia
        normalized = re.sub(r'-(sg|de|eu|us|asia)$', '', normalized)
        return normalized

    # Special handling for service accounts - extract just the account name
    if resource_type == 'Service Account':
        # Format: name@project-id.iam.gserviceaccount.com
        if '@' in normalized:
            account_name = normalized.split('@')[0]
            # Remove environment from account name
            for env in ['sandbox', 'staging', 'production', 'prod', 'stg', 'dev']:
                account_name = account_name.replace(f'-{env}', '')
                account_name = account_name.replace(f'{env}-', '')
            return account_name
        return normalized

    # Remove common environment prefixes
    env_prefixes = [
        'myproject-sandbox-', 'myproject-staging-', 'myproject-production-',
        'sandbox-', 'staging-', 'production-',
        'data-sandbox-', 'data-staging-', 'data-production-',
    ]

    for prefix in env_prefixes:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
            break

    # Remove environment suffixes
    env_suffixes = ['-sandbox', '-staging', '-production', '-prod', '-stg', '-dev']
    for suffix in env_suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
            break

    # For Cloud Run/Functions, also strip -sub suffixes (like my-service-pubsub2bq)
    # These are the same resource logically

    # For Pub/Sub subscriptions, normalize topic references and regional suffixes
    if resource_type == 'Pub/Sub Subscription':
        # Remove -sub suffix
        if normalized.endswith('-sub'):
            normalized = normalized[:-4]
        # Normalize regional suffixes like -sg (asia-southeast1), -de (europe-west3), -eu, -us, -asia
        # These patterns match subscriptions like "my-stream-sub-sg" and "my-stream-sub-de"
        normalized = re.sub(r'-sub-(sg|de|eu|us|asia)$', '-sub', normalized)
        normalized = re.sub(r'-(sg|de|eu|us|asia)$', '', normalized)

    # For storage buckets, handle special GCP patterns
    if resource_type == 'Storage Bucket':
        # Remove project numbers
        normalized = re.sub(r'^\d+_', '', normalized)
        # Normalize region names
        normalized = re.sub(r'asia[-_]southeast1[-_]', '', normalized)
        normalized = re.sub(r'europe[-_]west\d[-_]', '', normalized)
        normalized = re.sub(r'us[-_]central\d[-_]', '', normalized)
        # Remove gcf version patterns
        normalized = re.sub(r'-v2-', '-', normalized)
        normalized = re.sub(r'gcf-sources-\d+-', 'gcf-sources-', normalized)
        normalized = re.sub(r'gcf-v2-sources-\d+-', 'gcf-sources-', normalized)
        normalized = re.sub(r'gcf-v2-uploads-\d+-', 'gcf-uploads-', normalized)

    # For Artifact Registry, normalize region
    if resource_type == 'Artifact Registry':
        # The registry name itself is what matters, not the location
        pass

    return normalized


def extract_name_from_path(full_name: str) -> str:
    """Extract the simple name from a full GCP resource path"""
    if '/' in full_name:
        return full_name.split('/')[-1]
    return full_name


def load_resources_from_env(env_dir: Path) -> Dict[str, List[Tuple[str, str, str]]]:
    """
    Load all resources from an environment directory.
    Returns: Dict[resource_type] -> List[(original_name, normalized_name, location)]
    """
    resources_by_type = defaultdict(list)

    if not env_dir.exists():
        return resources_by_type

    # Define parsers for each file type
    file_parsers = {
        'api_gateway.json': ('API Gateway', lambda item: item.get('displayName') or extract_name_from_path(item.get('name', ''))),
        'artifact_repos.json': ('Artifact Registry', lambda item: extract_name_from_path(item.get('name', ''))),
        'buckets.json': ('Storage Bucket', lambda item: item.get('name', '')),
        'cloud_functions.json': ('Cloud Function', lambda item: extract_name_from_path(item.get('name', ''))),
        'cloud_run_services.json': ('Cloud Run', lambda item: item.get('metadata', {}).get('name', '')),
        'pubsub_topics.json': ('Pub/Sub Topic', lambda item: extract_name_from_path(item.get('name', ''))),
        'pubsub_subs.json': ('Pub/Sub Subscription', lambda item: extract_name_from_path(item.get('name', ''))),
        'scheduler.json': ('Cloud Scheduler', lambda item: extract_name_from_path(item.get('name', ''))),
        'sql_instances.json': ('Cloud SQL', lambda item: item.get('name', '')),
        'dataflow_jobs.json': ('Dataflow Job', lambda item: item.get('name', '')),
        'memorystore.json': ('Memorystore', lambda item: extract_name_from_path(item.get('name', ''))),
        'cloud_build_triggers.json': ('Cloud Build Trigger', lambda item: item.get('name', '')),
        'service_accounts.json': ('Service Account', lambda item: item.get('email', '')),
        'secrets.json': ('Secret', lambda item: extract_name_from_path(item.get('name', ''))),
    }

    for filename, (resource_type, name_extractor) in file_parsers.items():
        file_path = env_dir / filename
        if not file_path.exists():
            continue

        try:
            if file_path.stat().st_size == 0:
                continue

            with open(file_path, 'r') as f:
                data = json.load(f)

            if not data or (isinstance(data, list) and len(data) == 0):
                continue

            for item in data:
                original_name = name_extractor(item)
                if not original_name or original_name == 'N/A':
                    continue

                # Extract location
                location = 'N/A'
                if 'location' in item:
                    location = item['location']
                elif 'region' in item:
                    location = item['region']
                elif 'name' in item and '/locations/' in str(item['name']):
                    parts = item['name'].split('/locations/')
                    if len(parts) > 1:
                        location = parts[1].split('/')[0]
                elif resource_type == 'Cloud Run':
                    labels = item.get('metadata', {}).get('labels', {})
                    location = labels.get('cloud.googleapis.com/location', 'N/A')

                normalized_name = normalize_resource_name(original_name, resource_type)
                resources_by_type[resource_type].append((original_name, normalized_name, location))

        except Exception as e:
            print(f"Error loading {filename} from {env_dir}: {e}")
            continue

    return resources_by_type


def create_comparison_matrix(envs: List[str]) -> List[Dict]:
    """
    Create a comparison matrix of resources across environments.
    Returns a list of dicts ready for CSV export.
    """
    # Load resources from all environments
    all_env_resources = {}
    for env in envs:
        env_dir = Path(env)
        all_env_resources[env] = load_resources_from_env(env_dir)
        print(f"Loaded {sum(len(v) for v in all_env_resources[env].values())} resources from {env}")

    # Collect all unique (resource_type, normalized_name) pairs
    all_resource_keys = set()
    for env in envs:
        for resource_type, resources in all_env_resources[env].items():
            for original_name, normalized_name, location in resources:
                all_resource_keys.add((resource_type, normalized_name))

    # Build comparison matrix
    comparison_rows = []

    for resource_type, normalized_name in sorted(all_resource_keys):
        row = {
            'Resource Type': resource_type,
            'Normalized Name': normalized_name,
        }

        # For each environment, collect the original names and locations
        for env in envs:
            original_names = []
            locations = set()

            if resource_type in all_env_resources[env]:
                for orig_name, norm_name, location in all_env_resources[env][resource_type]:
                    if norm_name == normalized_name:
                        original_names.append(orig_name)
                        locations.add(location)

            # Mark presence with X or show count if multiple
            if len(original_names) == 0:
                row[f'{env.capitalize()}'] = ''
                row[f'{env.capitalize()} Name'] = ''
                row[f'{env.capitalize()} Location'] = ''
            elif len(original_names) == 1:
                row[f'{env.capitalize()}'] = 'X'
                row[f'{env.capitalize()} Name'] = original_names[0]
                row[f'{env.capitalize()} Location'] = ', '.join(sorted(locations))
            else:
                row[f'{env.capitalize()}'] = f'X ({len(original_names)})'
                row[f'{env.capitalize()} Name'] = original_names[0] + f' (+{len(original_names)-1} more)'
                row[f'{env.capitalize()} Location'] = ', '.join(sorted(locations))

        comparison_rows.append(row)

    return comparison_rows


def main():
    envs = ['sandbox', 'staging', 'production']

    print("=" * 140)
    print("GCP RESOURCE COMPARISON ACROSS ENVIRONMENTS")
    print("=" * 140)
    print()

    # Create comparison matrix
    comparison_rows = create_comparison_matrix(envs)

    # Write detailed CSV with all columns
    detailed_csv = Path('resource_comparison_detailed.csv')
    with open(detailed_csv, 'w') as f:
        # Write header
        headers = ['Resource Type', 'Normalized Name']
        for env in envs:
            headers.extend([f'{env.capitalize()}', f'{env.capitalize()} Name', f'{env.capitalize()} Location'])
        f.write(','.join(headers) + '\n')

        # Write rows
        for row in comparison_rows:
            values = [
                f'"{row["Resource Type"]}"',
                f'"{row["Normalized Name"]}"',
            ]
            for env in envs:
                values.append(f'"{row.get(f"{env.capitalize()}", "")}"')
                values.append(f'"{row.get(f"{env.capitalize()} Name", "")}"')
                values.append(f'"{row.get(f"{env.capitalize()} Location", "")}"')
            f.write(','.join(values) + '\n')

    print(f"Detailed comparison saved to: {detailed_csv}")

    # Write simplified pivot-style CSV (just X markers)
    pivot_csv = Path('resource_comparison_pivot.csv')
    with open(pivot_csv, 'w') as f:
        # Write header
        headers = ['Resource Type', 'Normalized Name', 'Sandbox', 'Staging', 'Production']
        f.write(','.join(headers) + '\n')

        # Write rows
        for row in comparison_rows:
            values = [
                f'"{row["Resource Type"]}"',
                f'"{row["Normalized Name"]}"',
                f'"{row.get("Sandbox", "")}"',
                f'"{row.get("Staging", "")}"',
                f'"{row.get("Production", "")}"',
            ]
            f.write(','.join(values) + '\n')

    print(f"Pivot-style comparison saved to: {pivot_csv}")

    # Print summary statistics
    print()
    print("=" * 140)
    print("SUMMARY STATISTICS")
    print("=" * 140)

    # Count resources by presence pattern
    sandbox_only = 0
    staging_only = 0
    production_only = 0
    all_three = 0
    sandbox_and_staging = 0
    sandbox_and_production = 0
    staging_and_production = 0

    for row in comparison_rows:
        has_sandbox = bool(row.get('Sandbox'))
        has_staging = bool(row.get('Staging'))
        has_production = bool(row.get('Production'))

        if has_sandbox and has_staging and has_production:
            all_three += 1
        elif has_sandbox and has_staging:
            sandbox_and_staging += 1
        elif has_sandbox and has_production:
            sandbox_and_production += 1
        elif has_staging and has_production:
            staging_and_production += 1
        elif has_sandbox:
            sandbox_only += 1
        elif has_staging:
            staging_only += 1
        elif has_production:
            production_only += 1

    print(f"\nTotal unique resources (normalized): {len(comparison_rows)}")
    print(f"\nResource distribution:")
    print(f"  In all three environments:     {all_three:>4}")
    print(f"  Sandbox + Staging only:        {sandbox_and_staging:>4}")
    print(f"  Sandbox + Production only:     {sandbox_and_production:>4}")
    print(f"  Staging + Production only:     {staging_and_production:>4}")
    print(f"  Sandbox only:                  {sandbox_only:>4}  <- Candidates for cleanup")
    print(f"  Staging only:                  {staging_only:>4}")
    print(f"  Production only:               {production_only:>4}")

    # Show resources only in sandbox
    print()
    print("=" * 140)
    print("RESOURCES ONLY IN SANDBOX (Cleanup Candidates)")
    print("=" * 140)

    sandbox_only_resources = defaultdict(list)
    for row in comparison_rows:
        if row.get('Sandbox') and not row.get('Staging') and not row.get('Production'):
            sandbox_only_resources[row['Resource Type']].append(row['Sandbox Name'])

    for resource_type in sorted(sandbox_only_resources.keys()):
        print(f"\n{resource_type} ({len(sandbox_only_resources[resource_type])}):")
        for name in sorted(sandbox_only_resources[resource_type])[:10]:  # Show first 10
            print(f"  - {name}")
        if len(sandbox_only_resources[resource_type]) > 10:
            print(f"  ... and {len(sandbox_only_resources[resource_type]) - 10} more")

    print()
    print("=" * 140)


if __name__ == '__main__':
    main()
