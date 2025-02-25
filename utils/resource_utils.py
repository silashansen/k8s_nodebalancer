import re

class ResourceUtils:
    """Utility functions for handling resource measurements."""
    
    @staticmethod
    def convert_memory_to_bytes(memory_str: str) -> int:
        """
        Convert memory string with units (Ki, Mi, Gi) to bytes.
        
        Args:
            memory_str: Memory string (e.g., '100Mi')
            
        Returns:
            Memory value in bytes
            
        Examples:
            '100Mi' -> 104857600
            '1Gi' -> 1073741824
        """
        match = re.match(r'(\d+)([KMG]i)', memory_str)
        if not match:
            return 0
            
        value, unit = match.groups()
        bytes_value = int(value)
        
        if unit == 'Ki':
            bytes_value *= 1024
        elif unit == 'Mi':
            bytes_value *= 1024 * 1024
        elif unit == 'Gi':
            bytes_value *= 1024 * 1024 * 1024
        
        return bytes_value 