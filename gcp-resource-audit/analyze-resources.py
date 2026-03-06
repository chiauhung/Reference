#!/usr/bin/env python3
"""
GCP Resource Analyzer
Analyzes exported GCP resources and displays name, location, created time, and updated time.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class ResourceInfo:
    def __init__(self, resource_type: str, name: str, location: str,
                 created: Optional[str], updated: Optional[str], environment: str = 'N/A'):
        self.resource_type = resource_type
        self.name = name
        self.location = location
        self.created = created
        self.updated = updated
        self.environment = environment

    def __repr__(self):
        return f"ResourceInfo({self.environment}, {self.resource_type}, {self.name}, {self.location}, {self.created}, {self.updated})"


def extract_location_from_path(name: str) -> str:
    """Extract location from GCP resource path (e.g., projects/.../locations/asia-southeast1/...)"""
    if '/locations/' in name:
        parts = name.split('/locations/')
        if len(parts) > 1:
            location = parts[1].split('/')[0]
            return location
    return 'N/A'


def parse_api_gateway(data: List[Dict]) -> List[ResourceInfo]:
    """Parse API Gateway resources"""
    resources = []
    for item in data:
        name = item.get('displayName') or item.get('name', 'N/A').split('/')[-1]
        location = extract_location_from_path(item.get('name', ''))
        created = item.get('createTime', 'N/A')
        updated = item.get('updateTime', 'N/A')
        resources.append(ResourceInfo('API Gateway', name, location, created, updated))
    return resources


def parse_artifact_registry(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Artifact Registry repositories"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A').split('/')[-1]
        location = extract_location_from_path(item.get('name', ''))
        created = item.get('createTime', 'N/A')
        updated = item.get('updateTime', 'N/A')
        resources.append(ResourceInfo('Artifact Registry', name, location, created, updated))
    return resources


def parse_buckets(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Cloud Storage buckets"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A')
        location = item.get('location', 'N/A')
        created = item.get('creation_time') or item.get('timeCreated', 'N/A')
        updated = item.get('updated_time') or item.get('updated', 'N/A')
        resources.append(ResourceInfo('Storage Bucket', name, location, created, updated))
    return resources


def parse_cloud_functions(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Cloud Functions"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A').split('/')[-1]
        location = extract_location_from_path(item.get('name', ''))
        created = item.get('createTime', 'N/A')
        updated = item.get('updateTime', 'N/A')
        resources.append(ResourceInfo('Cloud Function', name, location, created, updated))
    return resources


def parse_cloud_run(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Cloud Run services"""
    resources = []
    for item in data:
        metadata = item.get('metadata', {})
        name = metadata.get('name', 'N/A')
        labels = metadata.get('labels', {})
        location = labels.get('cloud.googleapis.com/location', 'N/A')
        created = metadata.get('creationTimestamp', 'N/A')

        # Cloud Run doesn't have updateTime in the same way, use generation or annotations
        annotations = metadata.get('annotations', {})
        updated = 'N/A'  # Cloud Run services don't have explicit update time in this export

        resources.append(ResourceInfo('Cloud Run', name, location, created, updated))
    return resources


def parse_pubsub_topics(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Pub/Sub topics"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A').split('/')[-1]
        location = 'global'  # Pub/Sub topics are global
        # Pub/Sub topics don't have creation/update timestamps in standard export
        resources.append(ResourceInfo('Pub/Sub Topic', name, location, 'N/A', 'N/A'))
    return resources


def parse_pubsub_subscriptions(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Pub/Sub subscriptions"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A').split('/')[-1]
        location = 'global'  # Pub/Sub subscriptions are global
        # Pub/Sub subscriptions don't have creation/update timestamps in standard export
        resources.append(ResourceInfo('Pub/Sub Subscription', name, location, 'N/A', 'N/A'))
    return resources


def parse_scheduler(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Cloud Scheduler jobs"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A').split('/')[-1]
        location = extract_location_from_path(item.get('name', ''))
        # Scheduler jobs don't have createTime in export
        created = 'N/A'
        updated = item.get('userUpdateTime', 'N/A')
        resources.append(ResourceInfo('Cloud Scheduler', name, location, created, updated))
    return resources


def parse_sql_instances(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Cloud SQL instances"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A')
        location = item.get('region', 'N/A')
        created = item.get('createTime', 'N/A')
        # SQL instances don't have explicit updateTime in standard export
        updated = 'N/A'
        resources.append(ResourceInfo('Cloud SQL', name, location, created, updated))
    return resources


def parse_app_engine_services(data: List[Dict]) -> List[ResourceInfo]:
    """Parse App Engine services"""
    resources = []
    for item in data:
        name = item.get('id') or item.get('name', 'N/A')
        location = 'N/A'  # App Engine location is at app level
        resources.append(ResourceInfo('App Engine Service', name, location, 'N/A', 'N/A'))
    return resources


def parse_app_engine_versions(data: List[Dict]) -> List[ResourceInfo]:
    """Parse App Engine versions"""
    resources = []
    for item in data:
        name = f"{item.get('service', 'N/A')}/{item.get('id', 'N/A')}"
        location = 'N/A'
        created = item.get('createTime', 'N/A')
        resources.append(ResourceInfo('App Engine Version', name, location, created, 'N/A'))
    return resources


def parse_cloud_build_triggers(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Cloud Build triggers"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A')
        location = extract_location_from_path(item.get('name', '')) if item.get('name') else 'global'
        created = item.get('createTime', 'N/A')
        updated = item.get('updateTime', 'N/A')
        resources.append(ResourceInfo('Cloud Build Trigger', name, location, created, updated))
    return resources


def parse_dataflow_jobs(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Dataflow jobs"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A')
        location = item.get('location', 'N/A')
        created = item.get('createTime', 'N/A')
        resources.append(ResourceInfo('Dataflow Job', name, location, created, 'N/A'))
    return resources


def parse_memorystore(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Memorystore instances"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A').split('/')[-1]
        location = extract_location_from_path(item.get('name', ''))
        created = item.get('createTime', 'N/A')
        resources.append(ResourceInfo('Memorystore', name, location, created, 'N/A'))
    return resources


def parse_service_accounts(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Service Accounts"""
    resources = []
    for item in data:
        email = item.get('email', 'N/A')
        # Service accounts are global
        location = 'global'
        created = 'N/A'  # Service accounts don't have explicit createTime in list output
        resources.append(ResourceInfo('Service Account', email, location, created, 'N/A'))
    return resources


def parse_secrets(data: List[Dict]) -> List[ResourceInfo]:
    """Parse Secrets"""
    resources = []
    for item in data:
        name = item.get('name', 'N/A').split('/')[-1]
        # Secrets are global but may have replication config
        location = 'global'
        created = item.get('createTime', 'N/A')
        resources.append(ResourceInfo('Secret', name, location, created, 'N/A'))
    return resources


def load_and_parse_file(file_path: Path, parser_func, environment: str) -> List[ResourceInfo]:
    """Load a JSON file and parse it with the given parser function"""
    try:
        if file_path.stat().st_size == 0:
            return []

        with open(file_path, 'r') as f:
            data = json.load(f)

        if not data or (isinstance(data, list) and len(data) == 0):
            return []

        resources = parser_func(data)
        # Add environment to each resource
        for resource in resources:
            resource.environment = environment
        return resources
    except Exception as e:
        print(f"Error parsing {file_path.name}: {e}")
        return []


def format_timestamp(ts: str) -> str:
    """Format timestamp to a more readable format"""
    if ts == 'N/A':
        return ts

    try:
        # Handle different timestamp formats
        if 'T' in ts:
            # ISO format: 2024-01-16T15:38:59.188233Z or 2024-09-11T06:53:02+0000
            if '+' in ts:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return ts
    except:
        return ts


def print_resources_table(resources: List[ResourceInfo], title: str):
    """Print resources in a formatted table"""
    if not resources:
        return

    print(f"\n{'=' * 140}")
    print(f"{title}")
    print(f"{'=' * 140}")
    print(f"{'Environment':<15} {'Resource Type':<25} {'Name':<30} {'Location':<20} {'Created':<20} {'Updated':<20}")
    print(f"{'-' * 140}")

    for resource in sorted(resources, key=lambda x: (x.environment, x.resource_type, x.name)):
        created = format_timestamp(resource.created)
        updated = format_timestamp(resource.updated)
        name = resource.name[:28] + '..' if len(resource.name) > 30 else resource.name
        print(f"{resource.environment:<15} {resource.resource_type:<25} {name:<30} {resource.location:<20} {created:<20} {updated:<20}")


def process_environment(env_dir: Path, environment: str, parsers: Dict) -> List[ResourceInfo]:
    """Process a single environment directory"""
    resources = []

    if not env_dir.exists():
        print(f"Warning: {env_dir} directory not found, skipping...")
        return resources

    for filename, parser in parsers.items():
        file_path = env_dir / filename
        if file_path.exists():
            env_resources = load_and_parse_file(file_path, parser, environment)
            resources.extend(env_resources)

    return resources


def main():
    # Define environments to process
    environments = ['sandbox', 'staging', 'production']

    # Map files to their parser functions
    parsers = {
        'api_gateway.json': parse_api_gateway,
        'artifact_repos.json': parse_artifact_registry,
        'buckets.json': parse_buckets,
        'cloud_functions.json': parse_cloud_functions,
        'cloud_run_services.json': parse_cloud_run,
        'pubsub_topics.json': parse_pubsub_topics,
        'pubsub_subs.json': parse_pubsub_subscriptions,
        'scheduler.json': parse_scheduler,
        'sql_instances.json': parse_sql_instances,
        'app_engine_services.json': parse_app_engine_services,
        'app_engine_versions.json': parse_app_engine_versions,
        'cloud_build_triggers.json': parse_cloud_build_triggers,
        'dataflow_jobs.json': parse_dataflow_jobs,
        'memorystore.json': parse_memorystore,
        'service_accounts.json': parse_service_accounts,
        'secrets.json': parse_secrets,
    }

    all_resources = []
    env_summaries = {}

    # Process each environment
    for env in environments:
        env_dir = Path(env)
        print(f"\nProcessing {env}...")
        env_resources = process_environment(env_dir, env, parsers)
        all_resources.extend(env_resources)
        env_summaries[env] = len(env_resources)

    # Print overall summary
    print(f"\n{'=' * 140}")
    print(f"GCP RESOURCES SUMMARY - ALL ENVIRONMENTS")
    print(f"{'=' * 140}")
    print(f"Total resources found: {len(all_resources)}")

    print(f"\nResources by environment:")
    for env, count in env_summaries.items():
        print(f"  {env:<15} {count:>4} resources")

    # Count by type across all environments
    type_counts = {}
    for resource in all_resources:
        type_counts[resource.resource_type] = type_counts.get(resource.resource_type, 0) + 1

    print(f"\nResources by type (across all environments):")
    for resource_type, count in sorted(type_counts.items()):
        print(f"  {resource_type:<25} {count:>4}")

    # Count by environment and type
    env_type_counts = {}
    for resource in all_resources:
        key = (resource.environment, resource.resource_type)
        env_type_counts[key] = env_type_counts.get(key, 0) + 1

    print(f"\nResources by environment and type:")
    for env in environments:
        if env_summaries.get(env, 0) > 0:
            print(f"\n  {env.upper()}:")
            for resource_type in sorted(set(r.resource_type for r in all_resources if r.environment == env)):
                count = env_type_counts.get((env, resource_type), 0)
                print(f"    {resource_type:<25} {count:>4}")

    # Export combined CSV for all environments
    combined_csv_path = Path('all_environments_resources.csv')
    with open(combined_csv_path, 'w') as f:
        f.write("Environment,Resource Type,Name,Location,Created,Updated\n")
        for resource in sorted(all_resources, key=lambda x: (x.environment, x.resource_type, x.name)):
            f.write(f'"{resource.environment}","{resource.resource_type}","{resource.name}","{resource.location}","{resource.created}","{resource.updated}"\n')

    print(f"\n{'=' * 140}")
    print(f"Combined CSV (long form) saved to: {combined_csv_path}")
    print(f"This file is ready for pivot table analysis!")
    print(f"{'=' * 140}")


if __name__ == '__main__':
    main()
