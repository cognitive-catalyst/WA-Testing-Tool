from typing import List, Dict, Any
import pandas as pd
from .base import OutputHandler


class DataFrameOutputHandler(OutputHandler):
    """Returns data as a pandas DataFrame."""
    
    def handle(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert data to pandas DataFrame.
        
        Args:
            data: List of dictionaries containing the analysis data
            
        Returns:
            pandas DataFrame containing the data
        """
        return pd.DataFrame(data)
