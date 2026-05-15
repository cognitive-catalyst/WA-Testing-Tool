from typing import Optional, Dict, List

from .data_types import BuiltInDataType, CustomDataType, DataType


class DataTypeRegistry:
    """Simple registry for managing custom data types."""
    
    def __init__(self):
        """Initialize an empty registry."""
        self.custom_types: Dict[str, CustomDataType] = {}
    
    def register(self, data: dict) -> CustomDataType:
        """Register a custom data type from a dictionary."""
        custom = CustomDataType.from_dict(data)
        self.custom_types[custom.id] = custom
        return custom
    
    def register_many(self, data_list: List[dict]) -> List[CustomDataType]:
        """Register multiple custom data types."""
        return [self.register(data) for data in data_list]
    
    def get_custom(self, type_id: str) -> Optional[CustomDataType]:
        """Get a custom data type by ID."""
        return self.custom_types.get(type_id)
    
    def resolve(self, type_id: str) -> DataType:
        """Resolve a data type ID to either a BuiltInDataType or CustomDataType."""
        # Try built-in types first
        try:
            return BuiltInDataType.from_id(type_id)
        except ValueError:
            pass
        
        # Try custom types
        custom = self.get_custom(type_id)
        if custom is not None:
            return custom
        
        # Not found
        raise ValueError(
            f"Unknown data type '{type_id}'. "
            f"Not a built-in type and not found in custom types registry."
        )
    
    def is_built_in(self, type_id: str) -> bool:
        """Check if a type ID is a built-in data type."""
        try:
            BuiltInDataType.from_id(type_id)
            return True
        except ValueError:
            return False
    
    def is_custom(self, type_id: str) -> bool:
        """Check if a type ID is a registered custom data type."""
        return type_id in self.custom_types
    
    def get_all_custom_types(self) -> List[CustomDataType]:
        """Get all registered custom data types."""
        return list(self.custom_types.values())
    
    def get_title(self, type_id: str) -> str:
        """Get a human-readable title for a data type."""
        try:
            data_type = self.resolve(type_id)
            return data_type.title
        except ValueError:
            # Unknown type
            return type_id
    
    def clear(self) -> None:
        """Clear all registered custom types."""
        self.custom_types.clear()
    
    def __len__(self) -> int:
        """Get the number of registered custom types."""
        return len(self.custom_types)
    
    def __contains__(self, type_id: str) -> bool:
        """Check if a custom type ID is registered."""
        return type_id in self.custom_types
    
    def __repr__(self) -> str:
        """Return a string representation of the registry."""
        return f"DataTypeRegistry(custom_types={len(self.custom_types)})"
    
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        if not self.custom_types:
            return "DataTypeRegistry (no custom types registered)"
        
        lines = [f"DataTypeRegistry with {len(self.custom_types)} custom type(s):"]
        for custom in self.custom_types.values():
            lines.append(f"  - {custom}")
        return "\n".join(lines)