import subprocess
from typing import List

class KubernetesClient:
    """Handles interactions with the Kubernetes cluster via kubectl."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the KubernetesClient.
        
        Args:
            dry_run: If True, will only simulate operations
        """
        self.dry_run = dry_run
    
    def execute_command(self, command: str) -> str:
        """
        Executes a kubectl command and returns the output.
        
        Args:
            command: The kubectl command to execute (without 'kubectl' prefix)
            
        Returns:
            The command output as a string
            
        Raises:
            Exception: If the kubectl command fails
        """
        full_command = ["kubectl"] + command.split()
        
        if self.dry_run and any(action in command for action in ["cordon", "uncordon", "delete"]):
            print(f"[DRY RUN] Would execute: kubectl {command}")
            return ""
            
        result = subprocess.run(full_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error executing kubectl command: {result.stderr}")
        return result.stdout

    def cordon_node(self, node: str) -> None:
        """Cordons a node to prevent new pods from being scheduled on it."""
        print(f"Cordoning {node}")
        self.execute_command(f"cordon {node}")

    def uncordon_node(self, node: str) -> None:
        """Uncordons a node to allow new pods to be scheduled on it."""
        print(f"Uncordoning {node}")
        self.execute_command(f"uncordon {node}")
        
    def delete_pod(self, pod_name: str, namespace: str) -> None:
        """Deletes a pod in the specified namespace."""
        print(f"Deleting pod {pod_name} in namespace {namespace}")
        self.execute_command(f"delete pod {pod_name} --namespace {namespace}") 