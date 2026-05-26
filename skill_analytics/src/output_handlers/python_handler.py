from typing import List, Dict, Any
from .base import OutputHandler


class PythonOutputHandler(OutputHandler):
    """Returns data as a list of dictionaries."""
    
    def handle(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Return data as-is (list of dicts).
        
        Args:
            data: List of dictionaries containing the analysis data
            
        Returns:
            The same list of dictionaries
        """
        return data



