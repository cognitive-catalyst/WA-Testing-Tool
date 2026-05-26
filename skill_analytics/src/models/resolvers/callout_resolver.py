from dataclasses import dataclass
from typing import List, Set

from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

from ..operands import create_operand_from_dict, Operand
from .base import Resolver, ResolverType


@dataclass
class ParameterMapping:
    """Represents a parameter mapping for callout requests."""
    parameter: str
    value: Operand
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ParameterMapping':
        """Create a ParameterMapping instance from a dictionary."""
        return cls(
            parameter=data["parameter"],
            value=create_operand_from_dict(data["value"])
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "parameter": self.parameter,
            "value": self.value.value
        }
    
    @property
    def spel_expression(self) -> str:
        """Generate the SpEL expression for this parameter mapping."""
        return f"{self.parameter} = {self.value.spel_expression}"

    def get_all_variable_ids(self) -> Set[str]:
        return self.value.get_all_variable_ids()


@dataclass
class RequestMapping:
    """Request mapping configuration for callout."""
    query: List[ParameterMapping]
    header: List[ParameterMapping]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RequestMapping':
        """Create a RequestMapping instance from a dictionary."""
        query = [ParameterMapping.from_dict(item) for item in data.get("query", [])]
        header = [ParameterMapping.from_dict(item) for item in data.get("header", [])]
        return cls(
            query=query, 
            header=header,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "query": [param.spel_expression for param in self.query],
            "header": [param.spel_expression for param in self.header],
            
        }

    def get_all_variable_ids(self) -> Set[str]:
        """Extract all variable IDs from query and header parameters."""
        """Extract all variable IDs from this parameter mapping."""
        variable_ids = set([])
        for param in self.query:
            variable_ids.update(param.get_all_variable_ids())
        for param in self.header:
            variable_ids.update(param.get_all_variable_ids())
        return variable_ids

@dataclass
class CalloutResolver(Resolver):
    """Resolver that calls an external extension."""
    path: str
    type: str
    method: str
    
    spec_hash_id: str
    catalog_item_id: str
    
    request_mapping: RequestMapping
    result_variable_id: str
    
    def __post_init__(self):
        """Set the resolver type after dataclass initialization."""
        self.resolver_type = ResolverType.CALLOUT
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CalloutResolver':
        """Create a CalloutResolver instance from a dictionary."""
        callout_data = data["callout"]
        return cls(
            path=callout_data["path"],
            type=callout_data["type"],
            method=callout_data["method"],
            
            spec_hash_id=callout_data["internal"]["spec_hash_id"],
            catalog_item_id=callout_data["internal"]["catalog_item_id"],
            
            request_mapping=RequestMapping.from_dict(callout_data["request_mapping"]),
            result_variable_id=callout_data["result_variable"],
        )
    
    def to_dict(self) -> dict:
        """Convert the resolver to a dictionary representation."""
        return {
            "type": self.resolver_type.id,
            "path": self.path,
            "type": self.type,
            "method": self.method,
            "spec_hash_id": self.spec_hash_id,
            "catalog_item_id": self.catalog_item_id,
            **self.request_mapping.to_dict(),
            "result_variable_id": self.result_variable_id,
        }
    
    def __repr__(self) -> str:
        return f"CalloutResolver(path={self.path}, method={self.method}, result_variable_id={self.result_variable_id})"
