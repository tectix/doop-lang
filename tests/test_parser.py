"""
Tests for the DOOP parser.
"""

import pytest
from doop.parser.lexer import Lexer, TokenType
from doop.parser.parser import Parser
from doop.utils.error_handling import ParserError
from doop.parser.ast import (
    Component, View, Property, Method, Relationship,
    Parameter, SequenceStep, Annotation
)


class TestParser:
    """Test cases for the DOOP parser."""
    
    def _parse(self, source):
        """Helper to parse a source string."""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_empty_input(self):
        """Test parsing an empty input."""
        ast = self._parse("")
        assert len(ast) == 0
    
    def test_basic_component(self):
        """Test parsing a basic component."""
        source = """
        component TestComponent {
            description: "A test component";
        }
        """
        
        ast = self._parse(source)
        
        # Check overall structure
        assert len(ast) == 1
        assert isinstance(ast[0], Component)
        
        # Check component details
        component = ast[0]
        assert component.name == "TestComponent"
        assert component.description == "A test component"
        assert len(component.properties) == 0
        assert len(component.methods) == 0
        assert len(component.relationships) == 0
        assert len(component.visualization) == 0
    
    def test_component_with_properties(self):
        """Test parsing a component with properties."""
        source = """
        component TestComponent {
            properties {
                name: String {
                    description: "Component name";
                    required: true;
                }
                
                count: Number {
                    description: "Count value";
                    default: "0";
                }
                
                simple: Boolean;
            }
        }
        """
        
        ast = self._parse(source)
        
        # Check overall structure
        assert len(ast) == 1
        assert isinstance(ast[0], Component)
        
        # Check component properties
        component = ast[0]
        assert len(component.properties) == 3
        
        # Check first property
        prop1 = component.properties[0]
        assert prop1.name == "name"
        assert prop1.type == "String"
        assert prop1.description == "Component name"
        assert prop1.required is True
        
        # Check second property
        prop2 = component.properties[1]
        assert prop2.name == "count"
        assert prop2.type == "Number"
        assert prop2.description == "Count value"
        assert prop2.default == "0"
        
        # Check third property (simple form)
        prop3 = component.properties[2]
        assert prop3.name == "simple"
        assert prop3.type == "Boolean"
        assert prop3.description is None
        assert not hasattr(prop3, 'default') or prop3.default is None
        assert not hasattr(prop3, 'required') or prop3.required is False
    
    def test_component_with_methods(self):
        """Test parsing a component with methods."""
        source = """
        component TestComponent {
            methods {
                simpleMethod() -> void {
                    description: "A simple method";
                }
                
                methodWithParams(param1: String, param2: Number) -> Boolean {
                    description: "Method with parameters";
                    precondition: "param1 must not be empty";
                    postcondition: "Returns true if successful";
                    returns: "Success status";
                }
                
                noReturnType() {
                    description: "Method without return type";
                }
                
                simpleDeclaration(id: String) -> Result;
            }
        }
        """
        
        ast = self._parse(source)
        
        # Check overall structure
        assert len(ast) == 1
        assert isinstance(ast[0], Component)
        
        # Check component methods
        component = ast[0]
        assert len(component.methods) == 4
        
        # Check first method
        method1 = component.methods[0]
        assert method1.name == "simpleMethod"
        assert len(method1.parameters) == 0
        assert method1.return_type == "void"
        assert method1.description == "A simple method"
        
        # Check second method
        method2 = component.methods[1]
        assert method2.name == "methodWithParams"
        assert len(method2.parameters) == 2
        assert method2.parameters[0].name == "param1"
        assert method2.parameters[0].type == "String"
        assert method2.parameters[1].name == "param2"
        assert method2.parameters[1].type == "Number"
        assert method2.return_type == "Boolean"
        assert method2.description == "Method with parameters"
        assert method2.precondition == "param1 must not be empty"
        assert method2.postcondition == "Returns true if successful"
        assert method2.returns == "Success status"
        
        # Check third method
        method3 = component.methods[2]
        assert method3.name == "noReturnType"
        assert len(method3.parameters) == 0
        assert method3.return_type is None
        assert method3.description == "Method without return type"
        
        # Check fourth method (simple form)
        method4 = component.methods[3]
        assert method4.name == "simpleDeclaration"
        assert len(method4.parameters) == 1
        assert method4.parameters[0].name == "id"
        assert method4.parameters[0].type == "String"
        assert method4.return_type == "Result"
        assert method4.description is None
    
    def test_component_with_relationships(self):
        """Test parsing a component with relationships."""
        source = """
        component TestComponent {
            relationships {
                depends_on: Component1 {
                    reason: "Required dependency";
                    description: "Used for core functionality";
                }
                
                provides: Component2, Component3 {
                    reason: "Service provision";
                }
                
                uses: Component4;
            }
        }
        """
        
        ast = self._parse(source)
        
        # Check overall structure
        assert len(ast) == 1
        assert isinstance(ast[0], Component)
        
        # Check component relationships
        component = ast[0]
        assert len(component.relationships) == 3
        
        # Check first relationship
        rel1 = component.relationships[0]
        assert rel1.type == "depends_on"
        assert rel1.targets == ["Component1"]
        assert rel1.reason == "Required dependency"
        assert rel1.description == "Used for core functionality"
        
        # Check second relationship
        rel2 = component.relationships[1]
        assert rel2.type == "provides"
        assert rel2.targets == ["Component2", "Component3"]
        assert rel2.reason == "Service provision"
        assert rel2.description is None
        
        # Check third relationship (simple form)
        rel3 = component.relationships[2]
        assert rel3.type == "uses"
        assert rel3.targets == ["Component4"]
        assert rel3.reason is None
        assert rel3.description is None
    
    def test_component_with_visualization(self):
        """Test parsing a component with visualization properties."""
        source = """
        component TestComponent {
            visualization {
                color: #3498db;
                icon: "database";
                group: "Infrastructure";
                order: 1;
            }
        }
        """
        
        ast = self._parse(source)
        
        # Check overall structure
        assert len(ast) == 1
        assert isinstance(ast[0], Component)
        
        # Check component visualization
        component = ast[0]
        assert len(component.visualization) == 4
        assert component.visualization["color"] == "#3498db"
        assert component.visualization["icon"] == "database"
        assert component.visualization["group"] == "Infrastructure"
        assert component.visualization["order"] == "1"
    
    def test_view(self):
        """Test parsing a view."""
        source = """
        view TestView {
            description: "A test view";
            includes: Component1, Component2, Component3;
            focus: "Key interactions";
            
            sequence {
                Component1 -> Component2: "request()";
                Component2 -> Component3: "process()";
                Component3 -> Component2: "response()";
                Component2 -> Component1: "result()";
            }
        }
        """
        
        ast = self._parse(source)
        
        # Check overall structure
        assert len(ast) == 1
        assert isinstance(ast[0], View)
        
        # Check view details
        view = ast[0]
        assert view.name == "TestView"
        assert view.description == "A test view"
        assert view.includes == ["Component1", "Component2", "Component3"]
        assert view.focus == "Key interactions"
        
        # Check sequence
        assert len(view.sequence) == 4
        
        # Check first sequence step
        step1 = view.sequence[0]
        assert step1.source == "Component1"
        assert step1.target == "Component2"
        assert step1.message == "request()"
        
        # Check second sequence step
        step2 = view.sequence[1]
        assert step2.source == "Component2"
        assert step2.target == "Component3"
        assert step2.message == "process()"
        
        # Check third sequence step
        step3 = view.sequence[2]
        assert step3.source == "Component3"
        assert step3.target == "Component2"
        assert step3.message == "response()"
        
        # Check fourth sequence step
        step4 = view.sequence[3]
        assert step4.source == "Component2"
        assert step4.target == "Component1"
        assert step4.message == "result()"
    
    def test_annotations(self):
        """Test parsing components and views with annotations."""
        source = """
        @deprecated
        @integration(language: "javascript")
        component TestComponent {
            description: "A test component";
        }
        
        @experimental
        view TestView {
            description: "A test view";
            includes: TestComponent;
        }
        """
        
        ast = self._parse(source)
        
        # Check overall structure
        assert len(ast) == 2
        assert isinstance(ast[0], Component)
        assert isinstance(ast[1], View)
        
        # Check component annotations
        component = ast[0]
        assert len(component.annotations) == 2
        assert component.annotations[0].name == "deprecated"
        assert component.annotations[1].name == "integration"
        assert component.annotations[1].args == {"language": "javascript"}
        
        # Check view annotations
        view = ast[1]
        assert len(view.annotations) == 1
        assert view.annotations[0].name == "experimental"
    
    def test_complete_example(self):
        """Test parsing a complete example."""
        source = """
        component UserService {
          description: "Service for managing users";
          
          properties {
            timeout: Number {
              description: "Connection timeout in seconds";
              default: "30";
            }
          }
          
          methods {
            createUser(userData: UserData) -> User {
              description: "Create a new user";
              returns: "Created user data";
            }
            
            getUserById(id: String) -> User {
              description: "Get user by ID";
              returns: "User data if found";
            }
          }
          
          relationships {
            depends_on: Database {
              reason: "For storing user data";
            }
          }
          
          visualization {
            color: #3498db;
            icon: "users";
            group: "Core Services";
          }
        }
        
        view UserManagement {
          description: "User management functionality";
          includes: UserService, Database;
        }
        """
        
        ast = self._parse(source)
        
        # Check overall structure
        assert len(ast) == 2
        assert isinstance(ast[0], Component)
        assert isinstance(ast[1], View)
        
        # Check component details
        component = ast[0]
        assert component.name == "UserService"
        assert component.description == "Service for managing users"
        assert len(component.properties) == 1
        assert len(component.methods) == 2
        assert len(component.relationships) == 1
        assert len(component.visualization) == 3
        
        # Check property
        prop = component.properties[0]
        assert prop.name == "timeout"
        assert prop.type == "Number"
        assert prop.description == "Connection timeout in seconds"
        assert prop.default == "30"
        
        # Check methods
        method1 = component.methods[0]
        assert method1.name == "createUser"
        assert len(method1.parameters) == 1
        assert method1.parameters[0].name == "userData"
        assert method1.parameters[0].type == "UserData"
        assert method1.return_type == "User"
        
        method2 = component.methods[1]
        assert method2.name == "getUserById"
        assert len(method2.parameters) == 1
        assert method2.parameters[0].name == "id"
        assert method2.parameters[0].type == "String"
        assert method2.return_type == "User"
        
        # Check relationship
        rel = component.relationships[0]
        assert rel.type == "depends_on"
        assert rel.targets == ["Database"]
        assert rel.reason == "For storing user data"
        
        # Check visualization
        assert component.visualization["color"] == "#3498db"
        assert component.visualization["icon"] == "users"
        assert component.visualization["group"] == "Core Services"
        
        # Check view
        view = ast[1]
        assert view.name == "UserManagement"
        assert view.description == "User management functionality"
        assert view.includes == ["UserService", "Database"]
    
    def test_parsing_errors(self):
        """Test handling of parsing errors."""
        # Test missing closing brace
        with pytest.raises(ParserError) as excinfo:
            self._parse("component TestComponent { description: \"Missing brace\";")
        assert "Expected RBRACE" in str(excinfo.value)
        
        # Test missing component name
        with pytest.raises(ParserError) as excinfo:
            self._parse("component { description: \"Missing name\"; }")
        assert "Expected component name" in str(excinfo.value)
        
        # Test missing semicolon
        with pytest.raises(ParserError) as excinfo:
            self._parse("component TestComponent { description: \"Missing semicolon\" }")
        assert "Expected SEMICOLON" in str(excinfo.value)
        
        # Test invalid relationship target
        with pytest.raises(ParserError) as excinfo:
            self._parse("component TestComponent { relationships { depends_on: ; } }")
        assert "Expected target component name" in str(excinfo.value)
        
        # Test invalid visualization property
        with pytest.raises(ParserError) as excinfo:
            self._parse("component TestComponent { visualization { color: \"Not a hex color\"; } }")
        assert "Expected HEX_COLOR" in str(excinfo.value)
    
    def test_multiple_components_and_views(self):
        """Test parsing multiple components and views."""
        source = """
        component Component1 {
            description: "First component";
        }
        
        component Component2 {
            description: "Second component";
        }
        
        view View1 {
            includes: Component1;
        }
        
        view View2 {
            includes: Component2;
        }
        """
        
        ast = self._parse(source)
        
        # Check overall structure
        assert len(ast) == 4
        assert isinstance(ast[0], Component)
        assert isinstance(ast[1], Component)
        assert isinstance(ast[2], View)
        assert isinstance(ast[3], View)
        
        # Check names
        assert ast[0].name == "Component1"
        assert ast[1].name == "Component2"
        assert ast[2].name == "View1"
        assert ast[3].name == "View2"