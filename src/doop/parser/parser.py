"""
Parser for the DOOP language.

This module provides a parser that converts a stream of tokens from the lexer into an
Abstract Syntax Tree (AST) representing the structure of a DOOP program.
"""

from typing import List, Dict, Any, Optional, Union
import ast

from doop.parser.lexer import Token, TokenType, LexerError
from doop.utils.error_handling import ParserError
from doop.parser.ast import (
    ASTNode, Component, View, Property, Method, Relationship,
    Parameter, SequenceStep, Annotation, IntegrationBlock
)


class Parser:
    """
    Parses DOOP source code into an Abstract Syntax Tree (AST).
    
    The parser takes a stream of tokens from the lexer and constructs an AST
    representing the structure of the DOOP program. It enforces the syntax rules
    of the language and detects syntax errors.
    """
    
    def __init__(self, tokens: List[Token]):
        """
        Initialize a new parser with a list of tokens.
        
        Args:
            tokens: List of tokens from the lexer
        """
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
    
    def error(self, message: str) -> None:
        """
        Raise a parser error with the current token's position.
        
        Args:
            message: Error message
            
        Raises:
            ParserError: With the provided message and current token's position
        """
        if self.current_token:
            line = self.current_token.line
            column = self.current_token.column
            file = self.current_token.file
            
            raise ParserError(message, file, line, column)
        else:
            raise ParserError(message)
    
    def eat(self, token_type: TokenType) -> Token:
        """
        Consume the current token if it matches the expected type.
        
        Args:
            token_type: The expected token type
            
        Returns:
            The consumed token
            
        Raises:
            ParserError: If the current token doesn't match the expected type
        """
        if self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name}")
    
    def advance(self) -> None:
        """
        Advance to the next token.
        
        Sets the current_token to the next token in the list,
        or None if we're at the end of the token list.
        """
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """
        Look ahead at a token without advancing.
        
        Args:
            offset: How many tokens ahead to look (default: 1)
            
        Returns:
            The token at the offset position, or None if beyond the token list
        """
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def parse(self) -> List[ASTNode]:
        """
        Parse the entire program.
        
        Returns:
            List of AST nodes representing the program
        """
        nodes = []
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            annotations = self.parse_annotations() if self.current_token.type == TokenType.AT else []
            
            if self.current_token.type == TokenType.COMPONENT:
                component = self.parse_component(annotations)
                nodes.append(component)
            elif self.current_token.type == TokenType.VIEW:
                view = self.parse_view(annotations)
                nodes.append(view)
            elif annotations:
                self.error("Annotations must be followed by a component or view definition")
            else:
                self.error(f"Expected 'component' or 'view', got {self.current_token.type.name}")
        
        return nodes
    
    def parse_annotations(self) -> List[Annotation]:
        """
        Parse annotations (@name(args)).
        
        Returns:
            List of Annotation objects
        """
        annotations = []
        
        while self.current_token and self.current_token.type == TokenType.AT:
            # Get position for error reporting
            position = (
                self.current_token.line,
                self.current_token.column
            )
            
            # Consume @
            self.eat(TokenType.AT)
            
            # Get annotation name
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected annotation name after @")
            
            name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            
            # Parse arguments if present
            args = {}
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                
                # Parse comma-separated arguments
                if self.current_token.type != TokenType.RPAREN:
                    while True:
                        # Parse key
                        if self.current_token.type != TokenType.IDENTIFIER:
                            self.error("Expected argument name")
                        
                        key = self.current_token.value
                        self.eat(TokenType.IDENTIFIER)
                        
                        # Parse =
                        if self.current_token.type != TokenType.COLON:
                            self.error("Expected ':' after argument name")
                        self.eat(TokenType.COLON)
                        
                        # Parse value
                        if self.current_token.type not in (
                            TokenType.STRING, TokenType.NUMBER, 
                            TokenType.BOOLEAN, TokenType.IDENTIFIER
                        ):
                            self.error("Expected argument value")
                        
                        value = self.current_token.value
                        self.eat(self.current_token.type)
                        
                        # Add to args
                        args[key] = value
                        
                        # Check for comma or end of args
                        if self.current_token.type == TokenType.COMMA:
                            self.eat(TokenType.COMMA)
                        else:
                            break
                
                self.eat(TokenType.RPAREN)
            
            # Create annotation
            annotation = Annotation(name, args, position)
            annotations.append(annotation)
        
        return annotations
    
    def parse_component(self, annotations: List[Annotation] = None) -> Component:
        """
        Parse a component definition.
        
        Args:
            annotations: Optional list of annotations preceding the component
            
        Returns:
            A Component AST node
        """
        # Get position for error reporting
        position = (
            self.current_token.line,
            self.current_token.column
        )
        
        # Consume 'component' keyword
        self.eat(TokenType.COMPONENT)
        
        # Parse component name
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected component name")
        
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Parse component body
        self.eat(TokenType.LBRACE)
        
        # Initialize component properties
        description = None
        properties = []
        methods = []
        relationships = []
        visualization = {}
        
        # Parse component body sections
        while self.current_token.type != TokenType.RBRACE:

            if self.current_token.type == TokenType.EOF:
                self.error("Expected RBRACE")

            # Parse description
            if self.current_token.type == TokenType.DESCRIPTION:
                self.eat(TokenType.DESCRIPTION)
                self.eat(TokenType.COLON)
                
                if self.current_token.type != TokenType.STRING:
                    self.error("Expected string for description")
                
                description = self.current_token.value
                self.eat(TokenType.STRING)
                self.eat(TokenType.SEMICOLON)
            
            # Parse properties section
            elif self.current_token.type == TokenType.PROPERTIES:
                properties = self.parse_properties_section()
            
            # Parse methods section
            elif self.current_token.type == TokenType.METHODS:
                methods = self.parse_methods_section()
            
            # Parse relationships section
            elif self.current_token.type == TokenType.RELATIONSHIPS:
                relationships = self.parse_relationships_section()
            
            # Parse visualization section
            elif self.current_token.type == TokenType.VISUALIZATION:
                visualization = self.parse_visualization_section()
            
            # Parse integration block 
            elif self.current_token.type == TokenType.AT:
                # Handle integration annotations (TODO: Implement)
                pass
            
            else:
                self.error(f"Unexpected token in component body: {self.current_token.type.name}")
        
        # Consume closing brace
        self.eat(TokenType.RBRACE)
        
        # Create component
        return Component(
            name=name,
            description=description,
            properties=properties,
            methods=methods,
            relationships=relationships,
            visualization=visualization,
            annotations=annotations or [],
            position=position
        )
    
    def parse_properties_section(self) -> List[Property]:
        """
        Parse a properties section.
        
        Returns:
            List of Property AST nodes
        """
        # Consume 'properties' keyword
        self.eat(TokenType.PROPERTIES)
        self.eat(TokenType.LBRACE)
        
        properties = []
        
        # Parse properties
        while self.current_token.type != TokenType.RBRACE:
            # Get position for error reporting
            position = (
                self.current_token.line,
                self.current_token.column
            )
            
            # Parse property name
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected property name")
            
            name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            
            # Parse property type
            self.eat(TokenType.COLON)
            
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected property type")
            
            type_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            
            # Check for collection types (List<Type>, Map<KeyType, ValueType>)
            if self.current_token.type == TokenType.LBRACE:
                # Property attributes
                self.eat(TokenType.LBRACE)
                
                description = None
                default = None
                required = False
                
                # Parse property attributes
                while self.current_token.type != TokenType.RBRACE:
                    # Parse description
                    if self.current_token.type == TokenType.DESCRIPTION:
                        self.eat(TokenType.DESCRIPTION)
                        self.eat(TokenType.COLON)
                        
                        if self.current_token.type != TokenType.STRING:
                            self.error("Expected string for description")
                        
                        description = self.current_token.value
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.SEMICOLON)
                    
                    # Parse default value
                    elif self.current_token.type == TokenType.DEFAULT:
                        self.eat(TokenType.DEFAULT)
                        self.eat(TokenType.COLON)
                        
                        if self.current_token.type not in (
                            TokenType.STRING, TokenType.NUMBER, TokenType.BOOLEAN
                        ):
                            self.error("Expected literal for default value")
                        
                        default = self.current_token.value
                        self.eat(self.current_token.type)
                        self.eat(TokenType.SEMICOLON)
                    
                    # Parse required flag
                    elif self.current_token.type == TokenType.REQUIRED:
                        self.eat(TokenType.REQUIRED)
                        self.eat(TokenType.COLON)
                        
                        if self.current_token.type != TokenType.BOOLEAN:
                            self.error("Expected boolean for required flag")
                        
                        required = self.current_token.value.lower() == 'true'
                        self.eat(TokenType.BOOLEAN)
                        self.eat(TokenType.SEMICOLON)
                    
                    else:
                        self.error(f"Unexpected token in property attributes: {self.current_token.type.name}")
                
                # Consume closing brace for property attributes
                self.eat(TokenType.RBRACE)
                
                # Create property
                property_node = Property(
                    name=name,
                    type=type_name,
                    description=description,
                    default=default,
                    required=required,
                    position=position
                )
                
                properties.append(property_node)
            
            else:
                # Simple property without attributes
                property_node = Property(
                    name=name,
                    type=type_name,
                    position=position
                )
                
                properties.append(property_node)
                
                # If there's a semicolon, consume it
                if self.current_token.type == TokenType.SEMICOLON:
                    self.eat(TokenType.SEMICOLON)
        
        # Consume closing brace for properties section
        self.eat(TokenType.RBRACE)
        
        return properties
    
    def parse_methods_section(self) -> List[Method]:
        """
        Parse a methods section.
        
        Returns:
            List of Method AST nodes
        """
        # Consume 'methods' keyword
        self.eat(TokenType.METHODS)
        self.eat(TokenType.LBRACE)
        
        methods = []
        
        # Parse methods
        while self.current_token.type != TokenType.RBRACE:
            # Get position for error reporting
            position = (
                self.current_token.line,
                self.current_token.column
            )
            
            # Parse method name
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected method name")
            
            name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            
            # Parse parameters
            self.eat(TokenType.LPAREN)
            parameters = []
            
            # Parse parameter list if not empty
            if self.current_token.type != TokenType.RPAREN:
                while True:
                    # Parse parameter name
                    if self.current_token.type != TokenType.IDENTIFIER:
                        self.error("Expected parameter name")
                    
                    param_name = self.current_token.value
                    param_position = (
                        self.current_token.line,
                        self.current_token.column
                    )
                    self.eat(TokenType.IDENTIFIER)
                    
                    # Parse parameter type
                    self.eat(TokenType.COLON)
                    
                    if self.current_token.type != TokenType.IDENTIFIER:
                        self.error("Expected parameter type")
                    
                    param_type = self.current_token.value
                    self.eat(TokenType.IDENTIFIER)
                    
                    # Create parameter
                    parameter = Parameter(
                        name=param_name,
                        type=param_type,
                        position=param_position
                    )
                    parameters.append(parameter)
                    
                    # Check for comma or end of parameters
                    if self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                    else:
                        break
            
            # Consume closing parenthesis
            self.eat(TokenType.RPAREN)
            
            # Parse return type if present
            return_type = None
            if self.current_token.type == TokenType.ARROW:
                self.eat(TokenType.ARROW)
                
                if self.current_token.type != TokenType.IDENTIFIER:
                    self.error("Expected return type")
                
                return_type = self.current_token.value
                self.eat(TokenType.IDENTIFIER)
            
            # Parse method attributes
            if self.current_token.type == TokenType.LBRACE:
                self.eat(TokenType.LBRACE)
                
                description = None
                precondition = None
                postcondition = None
                returns = None
                
                # Parse method attributes
                while self.current_token.type != TokenType.RBRACE:
                    # Parse description
                    if self.current_token.type == TokenType.DESCRIPTION:
                        self.eat(TokenType.DESCRIPTION)
                        self.eat(TokenType.COLON)
                        
                        if self.current_token.type != TokenType.STRING:
                            self.error("Expected string for description")
                        
                        description = self.current_token.value
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.SEMICOLON)
                    
                    # Parse precondition
                    elif self.current_token.type == TokenType.PRECONDITION:
                        self.eat(TokenType.PRECONDITION)
                        self.eat(TokenType.COLON)
                        
                        if self.current_token.type != TokenType.STRING:
                            self.error("Expected string for precondition")
                        
                        precondition = self.current_token.value
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.SEMICOLON)
                    
                    # Parse postcondition
                    elif self.current_token.type == TokenType.POSTCONDITION:
                        self.eat(TokenType.POSTCONDITION)
                        self.eat(TokenType.COLON)
                        
                        if self.current_token.type != TokenType.STRING:
                            self.error("Expected string for postcondition")
                        
                        postcondition = self.current_token.value
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.SEMICOLON)
                    
                    # Parse returns
                    elif self.current_token.type == TokenType.RETURNS:
                        self.eat(TokenType.RETURNS)
                        self.eat(TokenType.COLON)
                        
                        if self.current_token.type != TokenType.STRING:
                            self.error("Expected string for returns")
                        
                        returns = self.current_token.value
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.SEMICOLON)
                    
                    else:
                        self.error(f"Unexpected token in method attributes: {self.current_token.type.name}")
                
                # Consume closing brace for method attributes
                self.eat(TokenType.RBRACE)
                
                # Create method
                method = Method(
                    name=name,
                    parameters=parameters,
                    return_type=return_type,
                    description=description,
                    precondition=precondition,
                    postcondition=postcondition,
                    returns=returns,
                    position=position
                )
                
                methods.append(method)
            
            else:
                # Simple method without attributes
                method = Method(
                    name=name,
                    parameters=parameters,
                    return_type=return_type,
                    position=position
                )
                
                methods.append(method)
                
                # If there's a semicolon, consume it
                if self.current_token.type == TokenType.SEMICOLON:
                    self.eat(TokenType.SEMICOLON)
        
        # Consume closing brace for methods section
        self.eat(TokenType.RBRACE)
        
        return methods
    
    def parse_relationships_section(self) -> List[Relationship]:
        """
        Parse a relationships section.
        
        Returns:
            List of Relationship AST nodes
        """
        # Consume 'relationships' keyword
        self.eat(TokenType.RELATIONSHIPS)
        self.eat(TokenType.LBRACE)
        
        relationships = []
        
        # Parse relationships
        while self.current_token.type != TokenType.RBRACE:
            # Get position for error reporting
            position = (
                self.current_token.line,
                self.current_token.column
            )
            
            # Parse relationship type
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected relationship type")
            
            rel_type = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.COLON)
            
            # Parse relationship targets
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected target component name")
            
            targets = [self.current_token.value]
            self.eat(TokenType.IDENTIFIER)
            
            # Parse additional targets if present
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                
                if self.current_token.type != TokenType.IDENTIFIER:
                    self.error("Expected target component name")
                
                targets.append(self.current_token.value)
                self.eat(TokenType.IDENTIFIER)
            
            # Parse relationship attributes if present
            reason = None
            description = None
            
            if self.current_token.type == TokenType.LBRACE:
                self.eat(TokenType.LBRACE)
                
                # Parse relationship attributes
                while self.current_token.type != TokenType.RBRACE:
                    # Parse reason
                    if self.current_token.type == TokenType.REASON:
                        self.eat(TokenType.REASON)
                        self.eat(TokenType.COLON)
                        
                        if self.current_token.type != TokenType.STRING:
                            self.error("Expected string for reason")
                        
                        reason = self.current_token.value
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.SEMICOLON)
                    
                    # Parse description
                    elif self.current_token.type == TokenType.DESCRIPTION:
                        self.eat(TokenType.DESCRIPTION)
                        self.eat(TokenType.COLON)
                        
                        if self.current_token.type != TokenType.STRING:
                            self.error("Expected string for description")
                        
                        description = self.current_token.value
                        self.eat(TokenType.STRING)
                        self.eat(TokenType.SEMICOLON)
                    
                    else:
                        self.error(f"Unexpected token in relationship attributes: {self.current_token.type.name}")
                
                # Consume closing brace for relationship attributes
                self.eat(TokenType.RBRACE)
            
            # If no attributes but a semicolon is present, consume it
            elif self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            
            # Create relationship
            relationship = Relationship(
                type=rel_type,
                targets=targets,
                reason=reason,
                description=description,
                position=position
            )
            
            relationships.append(relationship)
        
        # Consume closing brace for relationships section
        self.eat(TokenType.RBRACE)
        
        return relationships
    
    def parse_visualization_section(self) -> Dict[str, Any]:
        """
        Parse a visualization section.
        
        Returns:
            Dictionary with visualization properties
        """
        # Consume 'visualization' keyword
        self.eat(TokenType.VISUALIZATION)
        self.eat(TokenType.LBRACE)
        
        visualization = {}
        
        # Parse visualization properties
        while self.current_token.type != TokenType.RBRACE:
            # Parse color
            if self.current_token.type == TokenType.COLOR:
                self.eat(TokenType.COLOR)
                self.eat(TokenType.COLON)
                
                if self.current_token.type != TokenType.HEX_COLOR:
                    self.error("Expected HEX_COLOR")
                
                visualization['color'] = self.current_token.value
                self.eat(TokenType.HEX_COLOR)
                self.eat(TokenType.SEMICOLON)
            
            # Parse icon
            elif self.current_token.type == TokenType.ICON:
                self.eat(TokenType.ICON)
                self.eat(TokenType.COLON)
                
                if self.current_token.type != TokenType.STRING:
                    self.error("Expected string for icon name")
                
                visualization['icon'] = self.current_token.value
                self.eat(TokenType.STRING)
                self.eat(TokenType.SEMICOLON)
            
            # Parse group
            elif self.current_token.type == TokenType.GROUP:
                self.eat(TokenType.GROUP)
                self.eat(TokenType.COLON)
                
                if self.current_token.type != TokenType.STRING:
                    self.error("Expected string for group name")
                
                visualization['group'] = self.current_token.value
                self.eat(TokenType.STRING)
                self.eat(TokenType.SEMICOLON)
            
            # Parse order
            elif self.current_token.type == TokenType.ORDER:
                self.eat(TokenType.ORDER)
                self.eat(TokenType.COLON)
                
                if self.current_token.type != TokenType.NUMBER:
                    self.error("Expected number for order")
                
                visualization['order'] = self.current_token.value
                self.eat(TokenType.NUMBER)
                self.eat(TokenType.SEMICOLON)
            
            else:
                self.error(f"Unexpected token in visualization section: {self.current_token.type.name}")
        
        # Consume closing brace for visualization section
        self.eat(TokenType.RBRACE)
        
        return visualization
    
    def parse_view(self, annotations: List[Annotation] = None) -> View:
        """
        Parse a view definition.
        
        Args:
            annotations: Optional list of annotations preceding the view
            
        Returns:
            A View AST node
        """
        # Get position for error reporting
        position = (
            self.current_token.line,
            self.current_token.column
        )
        
        # Consume 'view' keyword
        self.eat(TokenType.VIEW)
        
        # Parse view name
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected view name")
        
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Parse view body
        self.eat(TokenType.LBRACE)
        
        # Initialize view properties
        description = None
        includes = []
        focus = None
        sequence = []
        
        # Parse view body sections
        while self.current_token.type != TokenType.RBRACE:
            # Parse description
            if self.current_token.type == TokenType.DESCRIPTION:
                self.eat(TokenType.DESCRIPTION)
                self.eat(TokenType.COLON)
                
                if self.current_token.type != TokenType.STRING:
                    self.error("Expected string for description")
                
                description = self.current_token.value
                self.eat(TokenType.STRING)
                self.eat(TokenType.SEMICOLON)
            
            # Parse includes
            elif self.current_token.type == TokenType.INCLUDES:
                self.eat(TokenType.INCLUDES)
                self.eat(TokenType.COLON)
                
                # Parse first component
                if self.current_token.type != TokenType.IDENTIFIER:
                    self.error("Expected component name")
                
                includes = [self.current_token.value]
                self.eat(TokenType.IDENTIFIER)
                
                # Parse additional components
                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    
                    if self.current_token.type != TokenType.IDENTIFIER:
                        self.error("Expected component name")
                    
                    includes.append(self.current_token.value)
                    self.eat(TokenType.IDENTIFIER)
                
                self.eat(TokenType.SEMICOLON)
            
            # Parse focus
            elif self.current_token.type == TokenType.FOCUS:
                self.eat(TokenType.FOCUS)
                self.eat(TokenType.COLON)
                
                if self.current_token.type != TokenType.STRING:
                    self.error("Expected string for focus")
                
                focus = self.current_token.value
                self.eat(TokenType.STRING)
                self.eat(TokenType.SEMICOLON)
            
            # Parse sequence
            elif self.current_token.type == TokenType.SEQUENCE:
                sequence = self.parse_sequence_section()
            
            else:
                self.error(f"Unexpected token in view body: {self.current_token.type.name}")
        
        # Consume closing brace for view
        self.eat(TokenType.RBRACE)
        
        # Create view
        return View(
            name=name,
            description=description,
            includes=includes,
            focus=focus,
            sequence=sequence,
            annotations=annotations or [],
            position=position
        )
    
    def parse_sequence_section(self) -> List[SequenceStep]:
        """
        Parse a sequence section in a view.
        
        Returns:
            List of SequenceStep AST nodes
        """
        # Consume 'sequence' keyword
        self.eat(TokenType.SEQUENCE)
        self.eat(TokenType.LBRACE)
        
        steps = []
        
        # Parse sequence steps
        while self.current_token.type != TokenType.RBRACE:
            # Get position for error reporting
            position = (
                self.current_token.line,
                self.current_token.column
            )
            
            # Parse source
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected source component name")
            
            source = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            
            # Parse arrow
            self.eat(TokenType.ARROW)
            
            # Parse target
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected target component name")
            
            target = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            
            # Parse message (optional)
            message = None
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
                
                if self.current_token.type != TokenType.STRING:
                    self.error("Expected string for message")
                
                message = self.current_token.value
                self.eat(TokenType.STRING)
            
            # Consume semicolon
            self.eat(TokenType.SEMICOLON)
            
            # Create sequence step
            step = SequenceStep(
                source=source,
                target=target,
                message=message,
                position=position
            )
            
            steps.append(step)
        
        # Consume closing brace for sequence section
        self.eat(TokenType.RBRACE)
        
        return steps