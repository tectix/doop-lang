"""
Component Registry for DOOP language.
"""

from doop.parser.ast import Component


class ComponentRegistry:
    """
    Registry for DOOP components.
    
    The registry keeps track of all components defined in the system
    and provides methods to query relationships between them.
    """
    
    def __init__(self):
        """Initialize an empty component registry."""
        self.components = {}  
        self.relationships = []  
        self.views = {} 
        
    def register_component(self, component):
        """
        Add a component to the registry.
        
        Args:
            component (Component): The component to register
            
        Raises:
            ValueError: If a component with the same name already exists
        """
        if not isinstance(component, Component):
            raise TypeError(f"Expected Component object, got {type(component).__name__}")
            
        if component.name in self.components:
            raise ValueError(f"Duplicate component name: {component.name}")
        
        self.components[component.name] = component
        
        # Extract relationships
        for relationship in component.relationships:
            for target in relationship.targets:
                self.relationships.append((
                    component.name, 
                    relationship.type, 
                    target
                ))
    
    def register_view(self, view):
        """
        Add a view to the registry.
        
        Args:
            view (View): The view to register
            
        Raises:
            ValueError: If a view with the same name already exists
        """
        if view.name in self.views:
            raise ValueError(f"Duplicate view name: {view.name}")
        
        self.views[view.name] = view
    
    def get_component(self, name):
        """
        Retrieve a component by name.
        
        Args:
            name (str): The component name
            
        Returns:
            Component or None: The component if found, None otherwise
        """
        return self.components.get(name)
    
    def get_view(self, name):
        """
        Retrieve a view by name.
        
        Args:
            name (str): The view name
            
        Returns:
            View or None: The view if found, None otherwise
        """
        return self.views.get(name)
    
    def get_all_components(self):
        """
        Get all registered components.
        
        Returns:
            list[Component]: List of all components
        """
        return list(self.components.values())
    
    def get_all_views(self):
        """
        Get all registered views.
        
        Returns:
            list[View]: List of all views
        """
        return list(self.views.values())
    
    def get_related_components(self, name, relationship_type=None):
        """
        Find components related to the given component.
        
        Args:
            name (str): Name of the component to find relationships for
            relationship_type (str, optional): Filter by relationship type
            
        Returns:
            list[Component]: List of related components
        """
        related_names = []
        
        for source, rel_type, target in self.relationships:
            if source == name and (relationship_type is None or rel_type == relationship_type):
                related_names.append(target)
                
        return [self.components[rel_name] for rel_name in related_names 
                if rel_name in self.components]
    
    def get_referencing_components(self, name, relationship_type=None):
        """
        Find components that reference the given component.
        
        Args:
            name (str): Name of the component to find references to
            relationship_type (str, optional): Filter by relationship type
            
        Returns:
            list[Component]: List of components that reference this one
        """
        referencing_names = []
        
        for source, rel_type, target in self.relationships:
            if target == name and (relationship_type is None or rel_type == relationship_type):
                referencing_names.append(source)
                
        return [self.components[ref_name] for ref_name in referencing_names 
                if ref_name in self.components]
    
    def validate_relationships(self):
        """
        Validate that all relationships reference existing components.
        
        Returns:
            list[str]: List of error messages, empty if no errors
        """
        errors = []
        component_names = set(self.components.keys())
        
        for source, rel_type, target in self.relationships:
            if target not in component_names:
                errors.append(f"Component '{source}' has relationship to undefined component '{target}'")
                
        return errors
    
    def validate_views(self):
        """
        Validate that all views reference existing components.
        
        Returns:
            list[str]: List of error messages, empty if no errors
        """
        errors = []
        component_names = set(self.components.keys())
        
        for view_name, view in self.views.items():
            for included in view.includes:
                if included not in component_names:
                    errors.append(f"View '{view_name}' includes undefined component '{included}'")
                    
            if hasattr(view, 'sequence') and view.sequence:
                for step in view.sequence:
                    if step.source not in component_names and step.source != "User":
                        errors.append(f"View '{view_name}' has sequence with undefined source '{step.source}'")
                    if step.target not in component_names and step.target != "User":
                        errors.append(f"View '{view_name}' has sequence with undefined target '{step.target}'")
                        
        return errors