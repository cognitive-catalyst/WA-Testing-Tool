# analytics/analyzers/output_handlers/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum


class OutputFormat(Enum):
    """Enum for supported output formats."""
    PYTHON = "python"
    JSON = "json"
    DATAFRAME = "dataframe"
    CSV = "csv"


class OutputHandler(ABC):
    """Abstract base class for handling analysis output."""
    
    @abstractmethod
    def handle(self, data: List[Dict[str, Any]]) -> Any:
        """
        Process and return/save the data.
        
        Args:
            data: List of dictionaries containing the analysis data
            
        Returns:
            Processed data in the appropriate format
        """
        pass
