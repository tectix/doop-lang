"""
Abstract Syntax Tree (AST) definitions for DOOP language.
"""

class ASTNode:
    """Base class for all AST nodes."""
    def __init__(self, position=None):
        self.position = position 
        
    def __repr__(self):
        attrs = ', '.join(f"{key}={repr(value)}" for key, value in self.__dict__.items()
                         if key != 'position')
        return f"{self.__class__.__name__}({attrs})"


class Component(ASTNode):
    """Represents a component in DOOP."""
    def __init__(self, name, description=None, properties=None, methods=None, 
                 relationships=None, visualization=None, annotations=None, position=None):
        super().__init__(position)
        self.name = name
        self.description = description
        self.properties = properties or []
        self.methods = methods or []
        self.relationships = relationships or []
        self.visualization = visualization or {}
        self.annotations = annotations or []


class View(ASTNode):
    """Represents a view in DOOP."""
    def __init__(self, name, description=None, includes=None, focus=None, 
                 sequence=None, annotations=None, position=None):
        super().__init__(position)
        self.name = name
        self.description = description
        self.includes = includes or []
        self.focus = focus
        self.sequence = sequence or []
        self.annotations = annotations or []


class Property(ASTNode):
    """Represents a property in a component."""
    def __init__(self, name, type, description=None, default=None, 
                 required=False, annotations=None, position=None):
        super().__init__(position)
        self.name = name
        self.type = type
        self.description = description
        self.default = default
        self.required = required
        self.annotations = annotations or []


class Method(ASTNode):
    """Represents a method in a component."""
    def __init__(self, name, parameters=None, return_type=None, description=None, 
                 precondition=None, postcondition=None, returns=None, 
                 annotations=None, position=None):
        super().__init__(position)
        self.name = name
        self.parameters = parameters or []
        self.return_type = return_type
        self.description = description
        self.precondition = precondition
        self.postcondition = postcondition
        self.returns = returns
        self.annotations = annotations or []


class Parameter(ASTNode):
    """Represents a parameter in a method."""
    def __init__(self, name, type, default=None, position=None):
        super().__init__(position)
        self.name = name
        self.type = type
        self.default = default


class Relationship(ASTNode):
    """Represents a relationship between components."""
    def __init__(self, type, targets, reason=None, description=None, position=None):
        super().__init__(position)
        self.type = type  
        self.targets = targets 
        self.reason = reason
        self.description = description


class SequenceStep(ASTNode):
    """Represents a step in a sequence diagram."""
    def __init__(self, source, target, message, position=None):
        super().__init__(position)
        self.source = source
        self.target = target
        self.message = message


class Annotation(ASTNode):
    """Represents an annotation on a node."""
    def __init__(self, name, args=None, position=None):
        super().__init__(position)
        self.name = name
        self.args = args or {}


class IntegrationBlock(ASTNode):
    """Represents an integration block for code generation."""
    def __init__(self, language, name, code, position=None):
        super().__init__(position)
        self.language = language
        self.name = name
        self.code = code