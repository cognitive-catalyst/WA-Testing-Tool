from typing import Optional
from .base import OutputHandler, OutputFormat
from .python_handler import PythonOutputHandler
from .dataframe_handler import DataFrameOutputHandler
from .json_handler import JsonOutputHandler
from .csv_handler import CsvOutputHandler


def create_output_handler(
    output_format: OutputFormat | str,
    file_path: Optional[str] = None,
    **kwargs
) -> OutputHandler:
    """
    Factory function to create an output handler based on the specified format.
    
    Args:
        output_format: Type of output ("dict", "dataframe", "json", "csv")
        file_path: Optional file path for file-based outputs
        **kwargs: Additional arguments for specific handlers (e.g., indent, index)
        
    Returns:
        Appropriate OutputHandler instance
        
    Raises:
        ValueError: If output_format is not supported
    """
    if isinstance(output_format, str):
        try:
            output_format = OutputFormat(output_format)
        except:
            raise ValueError(
                f"Unsupported output format: {output_format}. "
                f"Supported formats: {', '.join([f.value for f in OutputFormat])}"
            )
    
    if output_format == OutputFormat.PYTHON:
        return PythonOutputHandler(**kwargs)
    elif output_format == OutputFormat.DATAFRAME:
        return DataFrameOutputHandler(**kwargs)
    elif output_format == OutputFormat.JSON:
        return JsonOutputHandler(file_path=file_path, **kwargs)
    elif output_format == OutputFormat.CSV:
        return CsvOutputHandler(file_path=file_path, **kwargs)
    else:
        raise ValueError(
            f"Unsupported output format: {output_format}. "
            f"Supported formats: {', '.join([f.value for f in OutputFormat])}"
        )
