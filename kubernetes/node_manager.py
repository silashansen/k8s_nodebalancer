import json
import os
from typing import List, Dict, Any

from kubernetes.client import KubernetesClient

class NodeManager:
    """Manages operations on Kubernetes nodes."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the NodeManager.
        
        Args:
            dry_run: If True, will only simulate operations
        """
        self.dry_run = dry_run
        self.node_groups = self._load_node_groups()
        self.k8s_client = KubernetesClient(dry_run)
    
    def _load_node_groups(self) -> Dict[str, List[str]]:
        """
        Load node groups from nodes.json file.
        
        Returns:
            Dictionary mapping group names to lists of node names
            
        Raises:
            FileNotFoundError: If nodes.json is not found
        """
        # Look for nodes.json in the current directory first, then in the package directory
        if os.path.exists('node_groups.json'):
            nodes_file = 'node_groups.json'
        else:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            nodes_file = os.path.join(script_dir, 'node_groups.json')
        
        with open(nodes_file, 'r') as f:
            return json.load(f)
    
    def get_available_groups(self) -> List[str]:
        """Returns a list of available node group names."""
        return list(self.node_groups.keys())
    
    def get_utilization_data(self) -> List[Dict[str, Any]]:
        """
        Gets memory and CPU usage for all nodes.
        
        Returns:
            List of dictionaries with node utilization data
        """
        output = self.k8s_client.execute_command("top nodes --no-headers")
        usage_data = []
        
        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
                
            node_name, memory_pct, cpu_pct = parts[0], parts[4], parts[2]
            memory_pct = int(memory_pct[:-1])  # Remove % and convert to int
            cpu_pct = int(cpu_pct[:-1])  # Remove % and convert to int
            
            usage_data.append({
                "name": node_name,
                "memory_pct": memory_pct,
                "cpu_pct": cpu_pct
            })
        
        return usage_data
    
    def get_node_stats(self, node_group: str) -> List[Dict[str, Any]]:
        """
        Get memory usage stats for nodes in the specified group.
        
        Args:
            node_group: Name of the node group
            
        Returns:
            List of node stats sorted by memory usage
            
        Raises:
            ValueError: If the node group is not found
        """
        usage_data = self.get_utilization_data()
        
        if node_group not in self.node_groups:
            raise ValueError(f"Node group '{node_group}' not found in nodes.json")
        
        # Filter nodes that belong to the specified group
        nodes = [node for node in usage_data if node["name"] in self.node_groups[node_group]]
        nodes.sort(key=lambda x: x["memory_pct"])
        return nodes
    
    def cordon_nodes(self, nodes: List[str]) -> None:
        """
        Cordons multiple nodes.
        
        Args:
            nodes: List of node names to cordon
        """
        for node in nodes:
            self.k8s_client.cordon_node(node)

    def uncordon_nodes(self, nodes: List[str]) -> None:
        """
        Uncordons multiple nodes.
        
        Args:
            nodes: List of node names to uncordon
        """
        for node in nodes:
            self.k8s_client.uncordon_node(node) 