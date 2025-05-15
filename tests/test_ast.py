"""
Tests for the Abstract Syntax Tree (AST) definitions.
"""

import pytest
from doop.parser.ast import (
    ASTNode, Component, View, Property, Method, 
    Parameter, Relationship, SequenceStep, Annotation
)


class TestASTNode:
    def test_base_node_initialization(self):
        node = ASTNode(position=(1, 2))
        assert node.position == (1, 2)
        
    def test_base_node_repr(self):
        node = ASTNode(position=(1, 2))
        repr_str = repr(node)
        assert "ASTNode" in repr_str
        assert "position" in repr_str


class TestComponent:
    def test_component_initialization(self):
        component = Component(
            name="TestComponent",
            description="A test component",
            properties=[Property("name", "String")],
            methods=[Method("test", [Parameter("arg", "String")], "void")],
            relationships=[Relationship("depends_on", ["OtherComponent"])],
            visualization={"color": "#ff0000"},
            annotations=[Annotation("deprecated")],
            position=(10, 5)
        )
        
        assert component.name == "TestComponent"
        assert component.description == "A test component"
        assert len(component.properties) == 1
        assert len(component.methods) == 1
        assert len(component.relationships) == 1
        assert component.visualization == {"color": "#ff0000"}
        assert len(component.annotations) == 1
        assert component.position == (10, 5)


class TestProperty:
    def test_property_initialization(self):
        prop = Property(
            name="testProp",
            type="String",
            description="A test property",
            default="default value",
            required=True,
            annotations=[Annotation("deprecated")],
            position=(15, 8)
        )
        
        assert prop.name == "testProp"
        assert prop.type == "String"
        assert prop.description == "A test property"
        assert prop.default == "default value"
        assert prop.required is True
        assert len(prop.annotations) == 1
        assert prop.position == (15, 8)


class TestMethod:
    def test_method_initialization(self):
        method = Method(
            name="testMethod",
            parameters=[
                Parameter("arg1", "String"),
                Parameter("arg2", "Number", default="0")
            ],
            return_type="Boolean",
            description="A test method",
            precondition="arg1 must not be empty",
            postcondition="Returns true if successful",
            returns="Success status",
            annotations=[Annotation("deprecated")],
            position=(20, 10)
        )
        
        assert method.name == "testMethod"
        assert len(method.parameters) == 2
        assert method.return_type == "Boolean"
        assert method.description == "A test method"
        assert method.precondition == "arg1 must not be empty"
        assert method.postcondition == "Returns true if successful"
        assert method.returns == "Success status"
        assert len(method.annotations) == 1
        assert method.position == (20, 10)


class TestRelationship:
    def test_relationship_initialization(self):
        rel = Relationship(
            type="depends_on",
            targets=["Component1", "Component2"],
            reason="Required dependencies",
            description="These components are required",
            position=(25, 12)
        )
        
        assert rel.type == "depends_on"
        assert rel.targets == ["Component1", "Component2"]
        assert rel.reason == "Required dependencies"
        assert rel.description == "These components are required"
        assert rel.position == (25, 12)


class TestView:
    def test_view_initialization(self):
        view = View(
            name="TestView",
            description="A test view",
            includes=["Component1", "Component2"],
            focus="Key interactions",
            sequence=[
                SequenceStep("Component1", "Component2", "getMessage()")
            ],
            annotations=[Annotation("deprecated")],
            position=(30, 15)
        )
        
        assert view.name == "TestView"
        assert view.description == "A test view"
        assert view.includes == ["Component1", "Component2"]
        assert view.focus == "Key interactions"
        assert len(view.sequence) == 1
        assert view.sequence[0].source == "Component1"
        assert view.sequence[0].target == "Component2"
        assert view.sequence[0].message == "getMessage()"
        assert len(view.annotations) == 1
        assert view.position == (30, 15)