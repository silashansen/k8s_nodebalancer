import time
from typing import List

from kubernetes.node_manager import NodeManager
from kubernetes.pod_manager import PodManager

class NodeBalancer:
    """Balances memory usage across nodes in a group."""
    
    max_cycles = 25  # Maximum number of balancing cycles to perform
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the NodeBalancer.
        
        Args:
            dry_run: If True, will only simulate operations
        """
        self.dry_run = dry_run
        self.node_manager = NodeManager(dry_run)
        self.pod_manager = PodManager(dry_run)
    
    def move_pods_from_high_to_low(self, pods_to_move: int, node_group: str) -> None:
        """
        Moves pods from the highest memory node to the lowest memory node.
        
        Args:
            pods_to_move: Number of pods to move
            node_group: Name of the node group
        """
        usage_data = self.node_manager.get_node_stats(node_group)
        
        if not usage_data:
            print(f"No nodes found in group {node_group}")
            return
            
        lowest_memory_node = min(usage_data, key=lambda x: x['memory_pct'])
        highest_memory_node = max(usage_data, key=lambda x: x['memory_pct'])

        print(f"Lowest memory node: {lowest_memory_node['name']} ({lowest_memory_node['memory_pct']}%)")
        print(f"Highest memory node: {highest_memory_node['name']} ({highest_memory_node['memory_pct']}%)")

        # Cordon all nodes except the lowest memory node
        nodes_to_cordon = [node["name"] for node in usage_data if node["name"] != lowest_memory_node["name"]]
        self.node_manager.cordon_nodes(nodes_to_cordon)
        
        # Delete pods from the highest memory node
        for _ in range(pods_to_move): 
            self.pod_manager.delete_highest_memory_pod(highest_memory_node)
        
        # Uncordon all nodes
        self.node_manager.uncordon_nodes(nodes_to_cordon)
    
    def balance_nodes(self, node_group: str, pods_to_move: int = 1, threshold: int = 10) -> None:
        """
        Balance nodes in the specified group.
        
        Args:
            node_group: Name of the node group
            pods_to_move: Number of pods to move in each iteration
            threshold: Memory percentage difference threshold to trigger balancing
        """
        cycles_completed = 0
        continue_balancing = True
        
        if self.dry_run:
            print("[DRY RUN] This is a simulation. No actual changes will be made.")
        
        print(f"Balancing nodes in group: {node_group}")
        
        # Continue while the difference between the highest and lowest memory usage 
        # is greater than threshold% and the number of cycles is less than max_cycles
        while continue_balancing and cycles_completed < self.max_cycles:
            try:
                node_stats = self.node_manager.get_node_stats(node_group)
                
                if not node_stats:
                    print(f"No nodes found in group {node_group}")
                    break
                    
                min_node = min(node_stats, key=lambda x: x['memory_pct'])
                max_node = max(node_stats, key=lambda x: x['memory_pct'])
                
                print(f"Node with lowest memory usage: {min_node['name']} ({min_node['memory_pct']}%)")
                print(f"Node with highest memory usage: {max_node['name']} ({max_node['memory_pct']}%)")
                
                memory_diff = max_node['memory_pct'] - min_node['memory_pct']
                
                # If the difference between the highest and lowest memory usage is greater than threshold%
                if memory_diff > threshold: 
                    print(f"Memory difference is {memory_diff}%, which exceeds threshold of {threshold}%")
                    print(f"Moving {pods_to_move} pods from {max_node['name']} to {min_node['name']}")
                    
                    self.move_pods_from_high_to_low(pods_to_move, node_group)
                    
                    if not self.dry_run:
                        print("Waiting for 1 minute before next iteration...")
                        time.sleep(60)
                    else:
                        print("[DRY RUN] Would wait for 1 minute before next iteration")
                    
                    continue_balancing = True
                else:
                    print(f"Memory difference is {memory_diff}%, which is below threshold of {threshold}%")
                    print("Balancing complete!")
                    continue_balancing = False
                
                cycles_completed += 1
                
            except Exception as e:
                print(f"Error during balancing cycle: {e}")
                break 