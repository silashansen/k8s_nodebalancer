import json
from typing import Dict, Any, Optional

from kubernetes.client import KubernetesClient
from utils.resource_utils import ResourceUtils

class PodManager:
    """Manages operations on Kubernetes pods."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the PodManager.
        
        Args:
            dry_run: If True, will only simulate operations
        """
        self.dry_run = dry_run
        self.k8s_client = KubernetesClient(dry_run)
    
    def find_highest_memory_pod(self, target_node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Finds the pod using the most memory on the specified node.
        
        Args:
            target_node: Node dictionary containing at least the 'name' key
            
        Returns:
            Dictionary with pod information or None if no pods found
        """
        # Fetch all pods across all namespaces with their node assignments
        pods_info = json.loads(self.k8s_client.execute_command("get pods --all-namespaces -o json"))
        pod_namespace_map = {}
        
        for item in pods_info['items']:
            node_name = item['spec'].get('nodeName')
            pod_name = item['metadata']['name']
            namespace = item['metadata']['namespace']
            
            if node_name == target_node["name"]:
                pod_namespace_map[pod_name] = namespace

        # Fetch memory usage of all pods
        pod_usage_output = self.k8s_client.execute_command("top pod --all-namespaces --no-headers")
        pod_resource_usage = []
        
        for line in pod_usage_output.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
                
            pod_utilization = {
                "namespace": parts[0],
                "pod_name": parts[1],
                "cpu_usage": parts[2],
                "memory_usage": ResourceUtils.convert_memory_to_bytes(parts[3]),
                "memory_usage_human": parts[3]
            }
        
            if pod_utilization["pod_name"] in pod_namespace_map:
                node_pod_namespace = pod_namespace_map[pod_utilization["pod_name"]]
                if node_pod_namespace == pod_utilization["namespace"]:
                    pod_resource_usage.append(pod_utilization)

        if not pod_resource_usage:
            return None
            
        return max(pod_resource_usage, key=lambda x: x["memory_usage"])
    
    def delete_highest_memory_pod(self, target_node: Dict[str, Any]) -> bool:
        """
        Deletes the pod using the most memory on the specified node.
        
        Args:
            target_node: Node dictionary containing at least the 'name' key
            
        Returns:
            True if a pod was deleted, False otherwise
        """
        pod_to_delete = self.find_highest_memory_pod(target_node)
        
        if pod_to_delete:
            print(f"Deleting pod {pod_to_delete['pod_name']} in namespace {pod_to_delete['namespace']} "
                  f"using {pod_to_delete['memory_usage_human']} from node {target_node['name']} due to high memory usage.")
            
            self.k8s_client.delete_pod(
                pod_to_delete['pod_name'], 
                pod_to_delete['namespace']
            )
            return True
        else:
            print(f"No high-memory pod found on node {target_node['name']} to delete.")
            return False 