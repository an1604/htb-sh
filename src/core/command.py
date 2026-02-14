# src/core/command.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re


@dataclass
class Parameter:
    """Command parameter definition"""
    name: str
    description: str
    required: bool = True
    default: Optional[str] = None


@dataclass
class Example:
    """Command example with expected output"""
    input: str
    output: str
    description: Optional[str] = None


@dataclass
class Command:
    """Command data model"""
    id: str
    name: str
    command: str  # Template with {param} placeholders
    explanation: str
    parameters: List[Parameter] = field(default_factory=list)
    examples: List[Example] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    
    def render(self, params: Dict[str, str]) -> str:
        """Render command template with provided parameters"""
        # Validate required parameters
        for param in self.parameters:
            if param.required and param.name not in params:
                if param.default:
                    params[param.name] = param.default
                else:
                    raise ValueError(f"Required parameter '{param.name}' not provided")
        
        # Substitute parameters
        rendered = self.command
        for key, value in params.items():
            rendered = rendered.replace(f"{{{key}}}", value)
        
        return rendered
    
    def get_parameter_placeholders(self) -> List[str]:
        """Extract parameter names from command template"""
        return re.findall(r'\{(\w+)\}', self.command)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'command': self.command,
            'explanation': self.explanation,
            'parameters': [
                {
                    'name': p.name,
                    'description': p.description,
                    'required': p.required,
                    'default': p.default
                } for p in self.parameters
            ],
            'examples': [
                {
                    'input': e.input,
                    'output': e.output,
                    'description': e.description
                } for e in self.examples
            ],
            'tags': self.tags,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Command':
        """Create Command from dictionary (YAML deserialization)"""
        parameters = [
            Parameter(**p) for p in data.get('parameters', [])
        ]
        examples = [
            Example(**e) for e in data.get('examples', [])
        ]
        
        return cls(
            id=data['id'],
            name=data['name'],
            command=data['command'],
            explanation=data['explanation'],
            parameters=parameters,
            examples=examples,
            tags=data.get('tags', []),
            notes=data.get('notes')
        )
