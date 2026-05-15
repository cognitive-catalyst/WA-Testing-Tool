from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from .base import OutputHandler


class JsonOutputHandler(OutputHandler):
    """Returns data as a JSON string or saves to file."""
    
    def __init__(self, file_path: Optional[str] = None, indent: int = 2):
        """
        Initialize JSON output handler.
        
        Args:
            file_path: Optional path to save JSON file. If None, returns JSON string.
            indent: Number of spaces for JSON indentation
        """
        self.file_path = file_path
        self.indent = indent
    
    def handle(self, data: List[Dict[str, Any]]) -> Optional[str]:
        """
        Convert data to JSON string or save to file.
        
        Args:
            data: List of dictionaries containing the analysis data
            
        Returns:
            JSON string if file_path is None, otherwise None (saves to file)
        """
        json_str = json.dumps(data, indent=self.indent)
        
        if self.file_path:
            Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w') as f:
                f.write(json_str)
            return None
        
        return json_str
