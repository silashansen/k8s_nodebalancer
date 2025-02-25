import subprocess
from typing import List

class KubernetesClient:
    """Handles interactions with the Kubernetes cluster via kubectl."""
    
    @staticmethod
    def execute_command(command: str, dry_run: bool = False) -> str:
        """
        Executes a kubectl command and returns the output.
        
        Args:
            command: The kubectl command to execute (without 'kubectl' prefix)
            dry_run: If True, will only print commands that would modify the cluster
            
        Returns:
            The command output as a string
            
        Raises:
            Exception: If the kubectl command fails
        """
        full_command = ["kubectl"] + command.split()
        
        if dry_run and any(action in command for action in ["cordon", "uncordon", "delete"]):
            print(f"[DRY RUN] Would execute: kubectl {command}")
            return ""
            
        result = subprocess.run(full_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error executing kubectl command: {result.stderr}")
        return result.stdout

    @classmethod
    def cordon_node(cls, node: str, dry_run: bool = False) -> None:
        """Cordons a node to prevent new pods from being scheduled on it."""
        print(f"Cordoning {node}")
        cls.execute_command(f"cordon {node}", dry_run)

    @classmethod
    def uncordon_node(cls, node: str, dry_run: bool = False) -> None:
        """Uncordons a node to allow new pods to be scheduled on it."""
        print(f"Uncordoning {node}")
        cls.execute_command(f"uncordon {node}", dry_run)
        
    @classmethod
    def delete_pod(cls, pod_name: str, namespace: str, dry_run: bool = False) -> None:
        """Deletes a pod in the specified namespace."""
        print(f"Deleting pod {pod_name} in namespace {namespace}")
        cls.execute_command(f"delete pod {pod_name} --namespace {namespace}", dry_run) 