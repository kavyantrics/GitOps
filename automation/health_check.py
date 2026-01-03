#!/usr/bin/env python3
"""
Health verification script for GitOps platform
Checks cluster health, pod status, and service availability
"""

import subprocess
import sys
import json
from typing import Dict, List

def run_kubectl_command(command: List[str]) -> Dict:
    """Run kubectl command and return JSON output"""
    try:
        result = subprocess.run(
            ['kubectl'] + command + ['-o', 'json'],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running kubectl: {e.stderr}")
        return {}
    except json.JSONDecodeError:
        print("Error parsing kubectl output")
        return {}

def check_cluster_connectivity() -> bool:
    """Check if we can connect to the cluster"""
    try:
        subprocess.run(
            ['kubectl', 'cluster-info'],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def check_node_status() -> Dict:
    """Check Kubernetes node status"""
    nodes = run_kubectl_command(['get', 'nodes'])
    node_status = {
        'total': 0,
        'ready': 0,
        'not_ready': 0
    }
    
    for node in nodes.get('items', []):
        node_status['total'] += 1
        conditions = node.get('status', {}).get('conditions', [])
        for condition in conditions:
            if condition.get('type') == 'Ready':
                if condition.get('status') == 'True':
                    node_status['ready'] += 1
                else:
                    node_status['not_ready'] += 1
    
    return node_status

def check_pod_status(namespace: str = 'default') -> Dict:
    """Check pod status in namespace"""
    pods = run_kubectl_command(['get', 'pods', '-n', namespace])
    pod_status = {
        'total': 0,
        'running': 0,
        'pending': 0,
        'failed': 0,
        'crash_loop_backoff': 0
    }
    
    for pod in pods.get('items', []):
        pod_status['total'] += 1
        phase = pod.get('status', {}).get('phase', 'Unknown')
        
        if phase == 'Running':
            pod_status['running'] += 1
        elif phase == 'Pending':
            pod_status['pending'] += 1
        elif phase == 'Failed':
            pod_status['failed'] += 1
        
        # Check for crash loop
        container_statuses = pod.get('status', {}).get('containerStatuses', [])
        for status in container_statuses:
            waiting = status.get('state', {}).get('waiting', {})
            if waiting.get('reason') == 'CrashLoopBackOff':
                pod_status['crash_loop_backoff'] += 1
    
    return pod_status

def check_service_endpoints(namespace: str = 'default') -> List[str]:
    """Check if services have endpoints"""
    services = run_kubectl_command(['get', 'services', '-n', namespace])
    endpoints = run_kubectl_command(['get', 'endpoints', '-n', namespace])
    
    endpoint_map = {}
    for ep in endpoints.get('items', []):
        name = ep.get('metadata', {}).get('name')
        subsets = ep.get('subsets', [])
        endpoint_map[name] = len(subsets) > 0
    
    services_without_endpoints = []
    for svc in services.get('items', []):
        name = svc.get('metadata', {}).get('name')
        if not endpoint_map.get(name, False):
            services_without_endpoints.append(name)
    
    return services_without_endpoints

def run_health_check(namespace: str = 'default'):
    """Run comprehensive health check"""
    print("GitOps Platform Health Check")
    print("=" * 60)
    
    # Check cluster connectivity
    print("\n1. Cluster Connectivity:")
    if check_cluster_connectivity():
        print("   ✓ Cluster is accessible")
    else:
        print("   ✗ Cannot connect to cluster")
        sys.exit(1)
    
    # Check nodes
    print("\n2. Node Status:")
    node_status = check_node_status()
    print(f"   Total nodes: {node_status['total']}")
    print(f"   Ready: {node_status['ready']}")
    print(f"   Not ready: {node_status['not_ready']}")
    
    if node_status['not_ready'] > 0:
        print("   ⚠ Warning: Some nodes are not ready")
    
    # Check pods
    print(f"\n3. Pod Status (namespace: {namespace}):")
    pod_status = check_pod_status(namespace)
    print(f"   Total pods: {pod_status['total']}")
    print(f"   Running: {pod_status['running']}")
    print(f"   Pending: {pod_status['pending']}")
    print(f"   Failed: {pod_status['failed']}")
    print(f"   CrashLoopBackOff: {pod_status['crash_loop_backoff']}")
    
    if pod_status['failed'] > 0 or pod_status['crash_loop_backoff'] > 0:
        print("   ⚠ Warning: Some pods are failing")
    
    # Check services
    print(f"\n4. Service Endpoints (namespace: {namespace}):")
    services_without_endpoints = check_service_endpoints(namespace)
    if services_without_endpoints:
        print(f"   ⚠ Warning: Services without endpoints: {', '.join(services_without_endpoints)}")
    else:
        print("   ✓ All services have endpoints")
    
    print("\n" + "=" * 60)
    
    # Overall health
    is_healthy = (
        node_status['not_ready'] == 0 and
        pod_status['failed'] == 0 and
        pod_status['crash_loop_backoff'] == 0 and
        len(services_without_endpoints) == 0
    )
    
    if is_healthy:
        print("✓ Overall Status: HEALTHY")
        sys.exit(0)
    else:
        print("✗ Overall Status: UNHEALTHY")
        sys.exit(1)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Health check for GitOps platform')
    parser.add_argument('--namespace', default='default', help='Kubernetes namespace to check')
    
    args = parser.parse_args()
    run_health_check(args.namespace)

