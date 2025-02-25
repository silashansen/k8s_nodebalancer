#!/usr/bin/env python3
import sys
import argparse
from balancer import NodeBalancer
from kubernetes.node_manager import NodeManager

class CustomArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser that provides more helpful error messages."""
    
    def error(self, message):
        """Override error method to print help when an error occurs."""
        sys.stderr.write(f'error: {message}\n')
        self.print_help()
        sys.exit(2)

def main():
    """Main entry point for the application."""
    # Get available node groups for help message
    node_manager = NodeManager()
    available_groups = node_manager.get_available_groups()
    
    # Create custom argument parser
    parser = CustomArgumentParser(description="Balance nodes in a Kubernetes cluster")
    
    # Add arguments
    parser.add_argument("node_group", help=f"Node group to balance. Available groups: {', '.join(available_groups)}")
    parser.add_argument("--threshold", "-t", type=int, default=10, help="Threshold for node balancing (default: 10)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Perform a dry run without making actual changes")
    
    try:
        # Parse arguments
        args = parser.parse_args()
        
        # Validate node group
        if args.node_group not in available_groups:
            print(f"Error: '{args.node_group}' is not a valid node group.")
            print(f"Available node groups: {', '.join(available_groups)}")
            sys.exit(1)
            
        balancer = NodeBalancer(args.dry_run)
        balancer.balance_nodes(args.node_group, threshold=args.threshold)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 