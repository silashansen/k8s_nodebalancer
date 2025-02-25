#!/usr/bin/env python3
import sys
from balancer import NodeBalancer
from kubernetes.node_manager import NodeManager

def main():
    """Main entry point for the application."""
    if len(sys.argv) < 2:
        node_manager = NodeManager()
        print("Usage: python -m node_balancer.main <node_group> [threshold] [--dry-run]")
        print("Available node groups: " + ", ".join(node_manager.get_available_groups()))
        sys.exit(1)
    
    # Parse arguments
    node_group = sys.argv[1]
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        sys.argv.remove("--dry-run")
    
    # Parse threshold if provided
    threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    try:
        balancer = NodeBalancer(dry_run)
        balancer.balance_nodes(node_group, threshold=threshold)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 