# Memory Balancer

This script balances the memory usage between nodes in a Kubernetes cluster by moving pods from nodes with high memory usage to nodes with low memory usage.
The routine will keep moving pods until the highest and lowest memory usage are within the defined threshold.

**Note:** This script is very brutal and will move *any* pods by brutally *deleting*, without paying attention to deployment strategies or similar.


# Node Groups

In the `node_groups.json` file, you MUST define the node groups you want to balance.
(Will add the ability to select groups based on node labels in the future.)

```json
{
    "controlplane": [
        "master-1",
        "master-2",
        "master-3"
    ],
    "non-production": [
        "worker-1",
        "worker-2",
        "worker-3",
        "worker-4",
        "worker-5"
    ],
    "production": [
        "worker-6",
        "worker-7"
    ]
}
```

## directory structure

```bash
.
├── kubernetes
│   ├── client.py
│   ├── node_manager.py
│   └── pod_manager.py
├── utils
│   ├── resource_utils.py
├── nodes.json
├── balancer.py
├── main.py
└── README.md
```

## Requirements

- Python 3.10+
- `kubectl` in the current PATH


## How to run

To balance the nodes once the difference between the highest and lowest memory usage is greater than 10%:

```
python3 main.py [-h] [--threshold THRESHOLD] [--dry-run] node_group

positional arguments:
  node_group            Node group to balance. Available groups: <groups_in_node_groups.json>

options:
  -h, --help            show this help message and exit
  --threshold, -t THRESHOLD
                        Threshold for node balancing (default: 10)
  --dry-run, -d         Perform a dry run without making actual changes
```

### Example

```bash
python3 main.py --dry-run --threshold 10 non-production
```
