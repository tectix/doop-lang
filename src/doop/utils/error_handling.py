"""
Error handling for DOOP language.

Provides consistent, user-friendly error reporting with context.
"""

import sys
import traceback
import os
import json
from typing import Optional, Dict, Any, List, Union, Tuple


class DoopError(Exception):
    """Base class for all DOOP errors."""
    
    def __init__(self, 
                 message: str, 
                 source: Optional[str] = None,
                 line: Optional[int] = None,
                 column: Optional[int] = None,
                 code: Optional[str] = None):
        """
        Initialize a DOOP error.
        
        Args:
            message: Error message
            source: Source file path
            line: Line number
            column: Column number
            code: Error code
        """
        self.message = message
        self.source = source
        self.line = line
        self.column = column
        self.code = code
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        """Format the error message with location information."""
        parts = []
        
        if self.source:
            parts.append(f"File: {self.source}")
        
        if self.line is not None:
            if self.column is not None:
                parts.append(f"Line {self.line}, Column {self.column}")
            else:
                parts.append(f"Line {self.line}")
        
        if self.code:
            parts.append(f"Error {self.code}")
        
        parts.append(self.message)
        
        return ": ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to a dictionary for JSON output."""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'source': self.source,
            'line': self.line,
            'column': self.column,
            'code': self.code
        }
    
    def get_suggestion(self) -> Optional[str]:
        """Get a suggestion for fixing the error."""
        return None


class LexerError(DoopError):
    """Error raised during lexical analysis."""
    
    ERROR_SUGGESTIONS = {
        "Invalid character": "Remove or replace the invalid character.",
        "Unclosed string literal": "Add a closing double quote to the string.",
        "Unclosed multi-line comment": "Add */ to close the multi-line comment.",
        "Invalid escape sequence": "Use valid escape sequences like \\n, \\t, \\\", or \\\\.",
        "Invalid hex color format": "Use the format #RRGGBB or #RGB for hex colors.",
        "Invalid hex digit": "Hex colors can only contain digits 0-9 and letters A-F."
    }
    
    def get_suggestion(self) -> Optional[str]:
        """Get a suggestion based on the error message."""
        for pattern, suggestion in self.ERROR_SUGGESTIONS.items():
            if pattern in self.message:
                return suggestion
        return None


class ParserError(DoopError):
    """Error raised during parsing."""
    
    ERROR_SUGGESTIONS = {
        "Expected LBRACE": "Add an opening brace '{'.",
        "Expected RBRACE": "Add a closing brace '}'.",
        "Expected COLON": "Add a colon ':' after the attribute name.",
        "Expected SEMICOLON": "Add a semicolon ';' at the end of the statement.",
        "Expected IDENTIFIER": "Use a valid identifier (starts with letter or underscore).",
        "Expected STRING": "Use a string literal enclosed in double quotes.",
        "Expected component name": "Provide a name for the component after the 'component' keyword.",
        "Expected view name": "Provide a name for the view after the 'view' keyword.",
        "Expected property name": "Provide a name for the property.",
        "Expected property type": "Specify the type of the property after the colon.",
        "Expected method name": "Provide a name for the method.",
        "Expected parameter name": "Provide a name for the parameter.",
        "Expected parameter type": "Specify the type of the parameter after the colon.",
        "Expected relationship type": "Use a valid relationship type like 'depends_on', 'provides', etc.",
        "Expected target component name": "Specify the target component for the relationship.",
        "Unexpected token": "Remove or replace the unexpected token with the expected one.",
    }
    
    def get_suggestion(self) -> Optional[str]:
        """Get a suggestion based on the error message."""
        for pattern, suggestion in self.ERROR_SUGGESTIONS.items():
            if pattern in self.message:
                return suggestion
        return None


class TypeError(DoopError):
    """Error raised during type checking."""
    
    ERROR_SUGGESTIONS = {
        "Unknown type": "Use a defined primitive type or component name.",
        "Invalid type": "Check the spelling of the type or define the component it references.",
        "Cannot cast": "Ensure the value is compatible with the target type."
    }
    
    def get_suggestion(self) -> Optional[str]:
        """Get a suggestion based on the error message."""
        for pattern, suggestion in self.ERROR_SUGGESTIONS.items():
            if pattern in self.message:
                return suggestion
        return None


class SemanticError(DoopError):
    """Error raised during semantic analysis."""
    
    ERROR_SUGGESTIONS = {
        "Undefined component": "Define the component or check for typos in the component name.",
        "Duplicate component name": "Use a unique name for each component.",
        "Duplicate property name": "Use a unique name for each property in the component.",
        "Duplicate method name": "Use a unique name for each method in the component.",
        "Invalid relationship type": "Use a supported relationship type: depends_on, provides, uses, extends, composed_of, or communicates_with.",
        "Invalid color format": "Use a valid hex color format like #3498db."
    }
    
    def get_suggestion(self) -> Optional[str]:
        """Get a suggestion based on the error message."""
        for pattern, suggestion in self.ERROR_SUGGESTIONS.items():
            if pattern in self.message:
                return suggestion
        return None


class ValidationError(DoopError):
    """Error raised during validation."""
    
    ERROR_SUGGESTIONS = {
        "undefined component": "Define the component or check for typos in the component name.",
        "includes undefined component": "Make sure all components referenced in views are defined.",
        "has sequence with undefined": "Make sure all components referenced in sequence are defined or use 'User' for external actors."
    }
    
    def get_suggestion(self) -> Optional[str]:
        """Get a suggestion based on the error message."""
        for pattern, suggestion in self.ERROR_SUGGESTIONS.items():
            if pattern in self.message:
                return suggestion
        return None


class GeneratorError(DoopError):
    """Error raised during document or diagram generation."""
    
    ERROR_SUGGESTIONS = {
        "Cannot create output directory": "Check if you have permission to create the directory or if the path is valid.",
        "Failed to generate diagram": "Ensure Graphviz is installed and the component structure is valid.",
        "Failed to generate documentation": "Check if you have permission to write to the output directory."
    }
    
    def get_suggestion(self) -> Optional[str]:
        """Get a suggestion based on the error message."""
        for pattern, suggestion in self.ERROR_SUGGESTIONS.items():
            if pattern in self.message:
                return suggestion
        return None


class ResourceError(DoopError):
    """Error raised when resource limits are exceeded."""
    
    ERROR_SUGGESTIONS = {
        "Component count limit exceeded": "Split your DOOP code into smaller files or increase the component limit.",
        "Timeout": "Simplify your DOOP code or increase the timeout limit.",
        "Memory limit exceeded": "Simplify your DOOP code or increase the memory limit."
    }
    
    def get_suggestion(self) -> Optional[str]:
        """Get a suggestion based on the error message."""
        for pattern, suggestion in self.ERROR_SUGGESTIONS.items():
            if pattern in self.message:
                return suggestion
        return None


class ErrorHandler:
    """
    Central handler for DOOP errors.
    
    This class provides methods for reporting and formatting errors.
    """
    
    def __init__(self, verbose: bool = False, json_output: bool = False):
        """
        Initialize the error handler.
        
        Args:
            verbose: Whether to display full error details
            json_output: Whether to format errors as JSON
        """
        self.verbose = verbose
        self.json_output = json_output
        self.errors: List[DoopError] = []
        self.source_cache: Dict[str, List[str]] = {}  # Cache for source files
    
    def add_error(self, error: DoopError) -> None:
        """
        Add an error to the collection.
        
        Args:
            error: The error to add
        """
        self.errors.append(error)
    
    def has_errors(self) -> bool:
        """
        Check if any errors have been recorded.
        
        Returns:
            True if errors exist, False otherwise
        """
        return len(self.errors) > 0
    
    def print_errors(self, file=sys.stderr) -> None:
        """
        Print all recorded errors.
        
        Args:
            file: File to print to (default: stderr)
        """
        if not self.errors:
            return
        
        if self.json_output:
            json.dump(
                {'errors': [e.to_dict() for e in self.errors]},
                file,
                indent=2
            )
            file.write('\n')
            return
        
        for i, error in enumerate(self.errors):
            if i > 0:
                file.write('\n')
            
            # Print error message
            file.write(f"Error: {error.format_message()}\n")
            
            # Print suggestion if available
            suggestion = error.get_suggestion()
            if suggestion:
                file.write(f"Suggestion: {suggestion}\n")
            
            # For verbose mode, show error context
            if self.verbose and error.source and error.line is not None:
                self._print_error_context(error, file)
    
    def _read_source_file(self, file_path: str) -> List[str]:
        """
        Read a source file and cache its contents.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            List of lines in the file
        """
        if file_path in self.source_cache:
            return self.source_cache[file_path]
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            self.source_cache[file_path] = lines
            return lines
        except Exception:
            return []
    
    def _print_error_context(self, error: DoopError, file=sys.stderr) -> None:
        """
        Print context for an error (source code excerpt).
        
        Args:
            error: The error
            file: File to print to
        """
        if not error.source or not os.path.isfile(error.source):
            return
        
        try:
            lines = self._read_source_file(error.source)
            
            start_line = max(0, error.line - 4)
            end_line = min(len(lines), error.line + 3)
            
            file.write("\nError context:\n")
            
            # Print context lines
            for i in range(start_line, end_line):
                # Line number and indicator
                line_num = i + 1  # Convert to 1-based
                if line_num == error.line:
                    prefix = f"{line_num:4d} >"
                else:
                    prefix = f"{line_num:4d}  "
                
                line_content = lines[i].rstrip('\n')
                
                file.write(f"{prefix} {line_content}\n")
                
                if line_num == error.line and error.column is not None:
                    underline = " " * (len(prefix) + error.column) + "^"
                    file.write(f"{underline}\n")
        except Exception:
            pass
    
    def get_errors_by_file(self) -> Dict[str, List[DoopError]]:
        """
        Group errors by source file.
        
        Returns:
            Dictionary mapping source files to lists of errors
        """
        result: Dict[str, List[DoopError]] = {}
        
        for error in self.errors:
            if error.source:
                if error.source not in result:
                    result[error.source] = []
                result[error.source].append(error)
            else:
                # Group errors without source under None
                if None not in result:
                    result[None] = []
                result[None].append(error)
        
        return result
    
    def generate_error_report(self) -> str:
        """
        Generate a detailed error report.
        
        Returns:
            Error report as a string
        """
        if not self.errors:
            return "No errors found."
        
        # Group errors by file
        errors_by_file = self.get_errors_by_file()
        
        # Build report
        report = [f"Error Report ({len(self.errors)} errors):\n"]
        
        # Add errors with source files
        for source, errors in errors_by_file.items():
            if source is None:
                continue  
            
            report.append(f"\nFile: {source}")
            report.append("-" * (len(source) + 6))
            
            # Sort errors by line number
            sorted_errors = sorted(errors, key=lambda e: (e.line or 0, e.column or 0))
            
            for error in sorted_errors:
                # Add line/column info
                location = ""
                if error.line is not None:
                    if error.column is not None:
                        location = f"Line {error.line}, Column {error.column}: "
                    else:
                        location = f"Line {error.line}: "
                
                # Add error details
                report.append(f"- {location}{error.message}")
                
                # Add suggestion if available
                suggestion = error.get_suggestion()
                if suggestion:
                    report.append(f"  Suggestion: {suggestion}")
        
        if None in errors_by_file and errors_by_file[None]:
            report.append("\nGeneral Errors:")
            report.append("--------------")
            
            for error in errors_by_file[None]:
                report.append(f"- {error.message}")
                
                suggestion = error.get_suggestion()
                if suggestion:
                    report.append(f"  Suggestion: {suggestion}")
        
        report.append(f"\nTotal errors: {len(self.errors)}")
        
        return "\n".join(report)
    
    def print_error_report(self, file=sys.stderr) -> None:
        """
        Print a detailed error report.
        
        Args:
            file: File to print to (default: stderr)
        """
        report = self.generate_error_report()
        file.write(report)
        file.write("\n")
    
    def save_error_report(self, file_path: str) -> None:
        """
        Save a detailed error report to a file.
        
        Args:
            file_path: Path to save the report to
        """
        report = self.generate_error_report()
        
        with open(file_path, 'w') as f:
            f.write(report)
    
    def handle_exception(self, exc: Exception, exit_code: int = 1) -> None:
        """
        Handle an exception by printing error and optionally exiting.
        
        Args:
            exc: The exception
            exit_code: Exit code to use if exiting
        """
        if isinstance(exc, DoopError):
            self.add_error(exc)
            self.print_errors()
        else:
            # Unexpected error
            if self.verbose:
                traceback.print_exc()
            else:
                error_type = exc.__class__.__name__
                print(f"Error: An unexpected {error_type} occurred: {str(exc)}", file=sys.stderr)
                print("Use --verbose for detailed error information", file=sys.stderr)
        
        sys.exit(exit_code)