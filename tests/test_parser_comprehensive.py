"""
Comprehensive tests for the DOOP parser.
Provides extended test coverage beyond the basic test cases.
"""

import pytest
from doop.parser.lexer import Lexer
from doop.parser.parser import Parser
from doop.utils.error_handling import ParserError
from doop.parser.ast import (
    Component, View, Property, Method, Relationship,
    Parameter, SequenceStep, Annotation
)


class TestParserComprehensive:
    """Extended test cases for the DOOP parser."""
    
    def _parse(self, source):
        """Helper to parse a source string."""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_complex_component_definition(self):
        """Test parsing a component with all possible sections and attributes."""
        source = """
        @deprecated
        @security(level: "high")
        component ComplexComponent {
            description: "A complex component with all attributes";
            
            properties {
                id: String {
                    description: "Unique identifier";
                    required: true;
                }
                count: Number {
                    description: "Item count";
                    default: "0";
                }
                flags: Boolean;
            }
            
            methods {
                findById(id: String) -> Entity {
                    description: "Find entity by ID";
                    precondition: "ID must not be empty";
                    postcondition: "Returns null if not found";
                    returns: "Entity or null";
                }
                
                update(entity: Entity, data: UpdateData) -> Boolean {
                    description: "Update entity with data";
                    returns: "Success status";
                }
                
                simple() -> void;
            }
            
            relationships {
                depends_on: Database, Logger {
                    reason: "Core dependencies";
                }
                
                provides: EntityService {
                    reason: "Main business service";
                    description: "Provides entity management";
                }
                
                uses: ConfigService;
            }
            
            visualization {
                color: #ff5500;
                icon: "database";
                group: "Core Services";
                order: 1;
            }
        }
        """
        
        ast = self._parse(source)
        
        # Validate component structure
        assert len(ast) == 1
        component = ast[0]
        
        # Check basic attributes
        assert component.name == "ComplexComponent"
        assert component.description == "A complex component with all attributes"
        
        # Check annotations
        assert len(component.annotations) == 2
        assert component.annotations[0].name == "deprecated"
        assert component.annotations[1].name == "security"
        assert component.annotations[1].args["level"] == "high"
        
        # Check properties
        assert len(component.properties) == 3
        assert component.properties[0].name == "id"
        assert component.properties[0].required is True
        assert component.properties[1].name == "count"
        assert component.properties[1].default == "0"
        
        # Check methods
        assert len(component.methods) == 3
        assert component.methods[0].name == "findById"
        assert len(component.methods[0].parameters) == 1
        assert component.methods[0].return_type == "Entity"
        assert component.methods[0].precondition == "ID must not be empty"
        
        # Check relationships
        assert len(component.relationships) == 3
        assert component.relationships[0].type == "depends_on"
        assert len(component.relationships[0].targets) == 2
        assert "Database" in component.relationships[0].targets
        assert "Logger" in component.relationships[0].targets
        
        # Check visualization
        assert component.visualization["color"] == "#ff5500"
        assert component.visualization["icon"] == "database"
    
    def test_nested_component_relationships(self):
        """Test components with complex relationships."""
        source = """
        component Parent {
            relationships {
                composed_of: Child1, Child2;
            }
        }
        
        component Child1 {
            relationships {
                depends_on: Database;
                communicates_with: Child2;
            }
        }
        
        component Child2 {
            relationships {
                provides: API;
            }
        }
        
        view SystemView {
            includes: Parent, Child1, Child2;
            
            sequence {
                Parent -> Child1: "request()";
                Child1 -> Child2: "process()";
                Child2 -> Child1: "response()";
                Child1 -> Parent: "result()";
            }
        }
        """
        
        ast = self._parse(source)
        
        assert len(ast) == 4
        
        view = next(node for node in ast if hasattr(node, 'includes'))
        
        assert len(view.sequence) == 4
        assert view.sequence[0].source == "Parent"
        assert view.sequence[0].target == "Child1"
    
    def test_complex_error_handling(self):
        """Test error reporting for various syntax errors."""
        with pytest.raises(ParserError) as excinfo:
            self._parse("""
            component Test {
                description: "Incomplete component";
                // Missing closing brace
            """)
        assert "Expected" in str(excinfo.value) or "Unexpected" in str(excinfo.value)
        
        with pytest.raises(ParserError) as excinfo:
            self._parse("""
            component Test {
                description: "Missing semicolon"
            }
            """)
        assert "Expected" in str(excinfo.value) or "Unexpected" in str(excinfo.value)
        
        with pytest.raises(ParserError) as excinfo:
            self._parse("""
            component Test {
                relationships {
                    depends_on: ;  // Missing target
                }
            }
            """)
        assert "Expected" in str(excinfo.value) or "Unexpected" in str(excinfo.value)
    
    def test_advanced_view_definition(self):
        """Test parsing advanced view definitions."""
        source = """
        view ComplexView {
            description: "A complex view definition";
            includes: ComponentA, ComponentB, ComponentC;
            focus: "Critical system interactions";
            
            sequence {
                // User initiated request flow
                User -> ComponentA: "request()";
                ComponentA -> ComponentB: "validate()";
                ComponentB -> ComponentC: "process()";
                
                // Response flow
                ComponentC -> ComponentB: "result()";
                ComponentB -> ComponentA: "response()";
                ComponentA -> User: "display()";
                
                // Error handling flow
                ComponentB -> ComponentA: "error()";
                ComponentA -> User: "showError()";
            }
        }
        """
        
        ast = self._parse(source)
        
        assert len(ast) == 1
        view = ast[0]
        
        assert view.name == "ComplexView"
        assert view.description == "A complex view definition"
        assert view.focus == "Critical system interactions"
        
        assert len(view.includes) == 3
        assert "ComponentA" in view.includes
        assert "ComponentB" in view.includes
        assert "ComponentC" in view.includes
        
        assert len(view.sequence) == 8
        
        assert view.sequence[0].source == "User"
        assert view.sequence[0].target == "ComponentA"
        assert view.sequence[0].message == "request()"
    
    def test_multiple_nested_components(self):
        """Test parsing multiple nested components with complex structure."""
        source = """
        component Database {
            description: "Database component";
        }
        
        component Cache {
            description: "Cache component";
        }
        
        component Service {
            description: "Service component";
            
            relationships {
                depends_on: Database, Cache;
            }
            
            methods {
                getData() -> Data;
                saveData(data: Data) -> Boolean;
            }
        }
        
        component API {
            description: "API component";
            
            relationships {
                depends_on: Service;
            }
            
            methods {
                handleRequest(req: Request) -> Response;
            }
        }
        
        view SystemView {
            includes: Database, Cache, Service, API;
        }
        
        view APIView {
            includes: API, Service;
        }
        """
        
        ast = self._parse(source)
        
        assert len(ast) == 6
        components = [node for node in ast if isinstance(node, Component)]
        views = [node for node in ast if isinstance(node, View)]
        assert len(components) == 4
        assert len(views) == 2
    
    def test_complex_annotations(self):
        """Test parsing complex annotations on various elements."""
        source = """
        @deprecated
        @version(major: "2", minor: "1", patch: "0")
        @author(name: "John Doe", email: "john@example.com")
        component AnnotatedComponent {
            description: "Annotated component";
            
            properties {
                id: String;
                name: String;
            }
            
            methods {
                getData() -> Result;
                processData(data: Data) -> void;
            }
        }
        """
        
        ast = self._parse(source)
        
        assert len(ast) == 1
        component = ast[0]
        
        assert len(component.annotations) == 3
        assert component.annotations[0].name == "deprecated"
        assert component.annotations[1].name == "version"
        assert component.annotations[1].args["major"] == "2"
        assert component.annotations[2].name == "author"
        assert "email" in component.annotations[2].args
    
    def test_simple_annotations(self):
        """Test parsing simple annotations."""
        source = """
        @simple
        component SimpleComponent {
            description: "Simple component";
        }
        """
        
        ast = self._parse(source)
        assert len(ast) == 1
        component = ast[0]
        assert len(component.annotations) == 1
        assert component.annotations[0].name == "simple"