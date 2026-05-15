from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from .base import OutputHandler


class CsvOutputHandler(OutputHandler):
    """Returns data as CSV string or saves to file."""
    
    def __init__(self, file_path: Optional[str] = None, index: bool = False):
        """
        Initialize CSV output handler.
        
        Args:
            file_path: Optional path to save CSV file. If None, returns CSV string.
            index: Whether to include index in CSV output
        """
        self.file_path = file_path
        self.index = index
    
    def handle(self, data: List[Dict[str, Any]]) -> Optional[str]:
        """
        Convert data to CSV string or save to file.
        
        Args:
            data: List of dictionaries containing the analysis data
            
        Returns:
            CSV string if file_path is None, otherwise None (saves to file)
        """
        df = pd.DataFrame(data)
        
        if self.file_path:
            Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.file_path, index=self.index)
            return None
        
        return df.to_csv(index=self.index)
