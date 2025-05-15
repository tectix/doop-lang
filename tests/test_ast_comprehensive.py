"""
Comprehensive tests for the Abstract Syntax Tree (AST) definitions.
Provides extended test coverage beyond the basic test cases.
"""

import pytest
from doop.parser.ast import (
    ASTNode, Component, View, Property, Method, 
    Parameter, Relationship, SequenceStep, Annotation
)


class TestASTComprehensive:
    """Extended test cases for DOOP AST classes."""
    
    def test_component_with_full_features(self):
        """Test Component object with all possible features."""
        
        component = Component(
            name="FullComponent",
            description="A fully featured component",
            properties=[
                Property("id", "String", description="Unique ID", required=True),
                Property("config", "Map", description="Configuration", default="{}")
            ],
            methods=[
                Method("initialize", [], "void", description="Initialize the component"),
                Method("process", [Parameter("data", "Object"), Parameter("options", "Options", default="null")], 
                      "Result", description="Process data", returns="Processing result")
            ],
            relationships=[
                Relationship("depends_on", ["Database", "Cache"], reason="Required services"),
                Relationship("provides", ["API"], description="Service API")
            ],
            visualization={"color": "#ff0000", "icon": "gear", "group": "Core"},
            annotations=[Annotation("version", {"major": "1", "minor": "0"})]
        )
        
        # Verify all properties were set correctly
        assert component.name == "FullComponent"
        assert len(component.properties) == 2
        assert len(component.methods) == 2
        assert len(component.relationships) == 2
        assert len(component.visualization) == 3
        assert len(component.annotations) == 1
        assert component.annotations[0].args["major"] == "1"
        
        # Check nested objects
        assert component.properties[0].name == "id"
        assert component.properties[0].required is True
        assert component.methods[1].parameters[0].name == "data"
        assert component.methods[1].parameters[1].default == "null"
        assert component.relationships[0].targets == ["Database", "Cache"]
    
    def test_view_with_complex_sequence(self):
        """Test View object with complex sequence."""
        
        view = View(
            name="ComplexView",
            description="A view with complex sequence",
            includes=["ComponentA", "ComponentB", "ComponentC"],
            focus="Critical path",
            sequence=[
                SequenceStep("User", "ComponentA", "request()"),
                SequenceStep("ComponentA", "ComponentB", "validate()"),
                SequenceStep("ComponentB", "ComponentC", "process()"),
                SequenceStep("ComponentC", "ComponentB", "result()"),
                SequenceStep("ComponentB", "ComponentA", "response()"),
                SequenceStep("ComponentA", "User", "display()")
            ],
            annotations=[Annotation("status", {"value": "draft"})]
        )
        
        assert view.name == "ComplexView"
        assert len(view.includes) == 3
        assert len(view.sequence) == 6
        assert view.sequence[0].source == "User"
        assert view.sequence[-1].target == "User"
        assert view.annotations[0].args["value"] == "draft"
        
        # Check sequence steps
        assert view.sequence[0].message == "request()"
        assert view.sequence[1].source == "ComponentA"
        assert view.sequence[1].target == "ComponentB"
        assert view.sequence[2].message == "process()"
        
        # Check circular flow
        assert view.sequence[0].target == view.sequence[5].source
        assert view.sequence[1].source == view.sequence[4].target
    
    def test_nested_parameters(self):
        """Test Method with nested parameter structures."""
        
        method = Method(
            name="complexOperation",
            parameters=[
                Parameter("config", "Config", default="default_config"),
                Parameter("callback", "Function"),
                Parameter("options", "Options", default="{timeout: 30}")
            ],
            return_type="ComplexResult",
            description="Complex operation with nested parameters",
            precondition="Config must be valid",
            postcondition="Result is properly formatted",
            returns="Structured result object or error"
        )
        
        assert method.name == "complexOperation"
        assert len(method.parameters) == 3
        assert method.parameters[0].default == "default_config"
        assert method.parameters[2].type == "Options"
        assert method.precondition == "Config must be valid"
        
        # Check parameter details
        param1 = method.parameters[0]
        assert param1.name == "config"
        assert param1.type == "Config"
        
        param3 = method.parameters[2]
        assert param3.name == "options"
        assert "{timeout: 30}" in param3.default
    
    def test_complex_annotations(self):
        """Test annotations with various argument structures."""
        
        annotations = [
            Annotation("deprecated"),
            Annotation("version", {"major": "1", "minor": "2", "patch": "3"}),
            Annotation("author", {"name": "John Doe", "email": "john@example.com"}),
            Annotation("security", {"level": "high", "audit": "true"}),
            Annotation("tags", {"values": "frontend,backend,api"})
        ]
        
        # Check basic annotation
        assert annotations[0].name == "deprecated"
        assert not annotations[0].args
        
        # Check version annotation
        assert annotations[1].name == "version"
        assert annotations[1].args["major"] == "1"
        assert annotations[1].args["minor"] == "2"
        assert annotations[1].args["patch"] == "3"
        
        # Check author annotation
        assert annotations[2].name == "author"
        assert annotations[2].args["name"] == "John Doe"
        assert annotations[2].args["email"] == "john@example.com"
        
        # Check security annotation
        assert annotations[3].name == "security"
        assert annotations[3].args["level"] == "high"
        
        # Check tags annotation
        assert annotations[4].name == "tags"
        assert "frontend" in annotations[4].args["values"]
    
    def test_component_with_complex_relationships(self):
        """Test component with complex relationships."""
        
        component = Component(
            name="ServiceComponent",
            description="A service component with complex relationships",
            relationships=[
                Relationship("depends_on", ["Database", "Cache", "Logger"], 
                             reason="Core infrastructure dependencies"),
                Relationship("uses", ["AuthService", "NotificationService"],
                             reason="External services",
                             description="Used for authentication and notifications"),
                Relationship("provides", ["UserAPI", "AdminAPI"],
                             description="Public APIs"),
                Relationship("communicates_with", ["MessageBus"],
                             reason="Event communication"),
                Relationship("composed_of", ["UserManager", "PermissionManager", "SessionManager"],
                             reason="Internal modules")
            ]
        )
        
        # Check relationships
        assert len(component.relationships) == 5
        
        # Check first relationship
        depends_on = component.relationships[0]
        assert depends_on.type == "depends_on"
        assert len(depends_on.targets) == 3
        assert "Database" in depends_on.targets
        assert "Logger" in depends_on.targets
        assert depends_on.reason == "Core infrastructure dependencies"
        
        # Check second relationship
        uses = component.relationships[1]
        assert uses.type == "uses"
        assert len(uses.targets) == 2
        assert uses.description == "Used for authentication and notifications"
        
        # Check composed_of relationship
        composed_of = component.relationships[4]
        assert composed_of.type == "composed_of"
        assert len(composed_of.targets) == 3
        assert "UserManager" in composed_of.targets
    
    def test_component_with_deep_nesting(self):
        """Test component with deeply nested structures."""
        
        component = Component(
            name="DeepComponent",
            description="Component with deep nesting",
            properties=[
                Property("config", "Config", 
                         description="Configuration object",
                         default="{timeout: 30, retry: true}",
                         required=True,
                         annotations=[
                             Annotation("validate"),
                             Annotation("format", {"type": "json"})
                         ])
            ],
            methods=[
                Method("process", 
                       parameters=[
                           Parameter("data", "Data"),
                           Parameter("options", "Options", default="{}")
                       ],
                       return_type="Result",
                       description="Process with options",
                       precondition="Data must be valid",
                       postcondition="Result is valid",
                       returns="Processed result",
                       annotations=[
                           Annotation("async"),
                           Annotation("cache", {"ttl": "3600"})
                       ])
            ],
            visualization={
                "color": "#ff00ff",
                "icon": "gear",
                "group": "Core",
                "order": "1"
            }
        )
        
        # Check property with annotations
        prop = component.properties[0]
        assert prop.name == "config"
        assert len(prop.annotations) == 2
        assert prop.annotations[0].name == "validate"
        assert prop.annotations[1].args["type"] == "json"
        
        # Check method with annotations
        method = component.methods[0]
        assert method.name == "process"
        assert len(method.parameters) == 2
        assert len(method.annotations) == 2
        assert method.annotations[0].name == "async"
        assert method.annotations[1].name == "cache"
        assert method.annotations[1].args["ttl"] == "3600"
        
        # Check visualization
        assert component.visualization["color"] == "#ff00ff"
        assert component.visualization["icon"] == "gear"
        assert component.visualization["group"] == "Core"
        assert component.visualization["order"] == "1"