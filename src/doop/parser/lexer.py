"""
Lexical analyzer for the DOOP language.

This module provides a lexer for tokenizing DOOP source code. It breaks the raw source
code into tokens which are then fed to the parser for syntactic analysis.
"""

from enum import Enum, auto
from typing import Optional, List, Dict, Tuple


class TokenType(Enum):
    """Token types for DOOP language."""
    # Keywords
    COMPONENT = auto()      # 'component' keyword
    VIEW = auto()           # 'view' keyword
    DESCRIPTION = auto()    # 'description' keyword
    PROPERTIES = auto()     # 'properties' keyword
    METHODS = auto()        # 'methods' keyword
    RELATIONSHIPS = auto()  # 'relationships' keyword 
    VISUALIZATION = auto()  # 'visualization' keyword
    SEQUENCE = auto()       # 'sequence' keyword
    FOCUS = auto()          # 'focus' keyword
    INCLUDES = auto()       # 'includes' keyword
    DEFAULT = auto()        # 'default' keyword
    REQUIRED = auto()       # 'required' keyword
    REASON = auto()         # 'reason' keyword
    RETURNS = auto()        # 'returns' keyword
    PRECONDITION = auto()   # 'precondition' keyword
    POSTCONDITION = auto()  # 'postcondition' keyword
    COLOR = auto()          # 'color' keyword
    ICON = auto()           # 'icon' keyword
    GROUP = auto()          # 'group' keyword
    ORDER = auto()          # 'order' keyword
    
    # Identifiers and literals
    IDENTIFIER = auto()     # variable/component names
    STRING = auto()         # string literals
    NUMBER = auto()         # number literals
    BOOLEAN = auto()        # true/false literals
    HEX_COLOR = auto()      # hex color literals like #FF00FF
    
    # Symbols
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    COLON = auto()          # :
    SEMICOLON = auto()      # ;
    COMMA = auto()          # ,
    ARROW = auto()          # ->
    AT = auto()             # @
    
    # Special
    EOF = auto()            # end of file
    COMMENT = auto()        # comment


class Token:
    """
    Represents a token in the DOOP language.
    
    A token is a categorized unit of source code like a keyword, identifier,
    symbol, or literal. Tokens include source position information for error reporting.
    """
    def __init__(self, type_: TokenType, value: str, line: int, column: int, file: Optional[str] = None):
        """
        Initialize a new token.
        
        Args:
            type_: The token type from TokenType enum
            value: The string value of the token
            line: Line number where the token appears (1-based)
            column: Column number where the token starts (1-based)
            file: Optional source file name
        """
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
        self.file = file
        
    def __repr__(self):
        """String representation of the token for debugging."""
        pos = f"{self.line}:{self.column}"
        if self.file:
            pos = f"{self.file}:{pos}"
        return f"Token({self.type.name}, '{self.value}', {pos})"
    
    def get_position(self) -> Tuple[int, int]:
        """Get the position of this token as a (line, column) tuple."""
        return (self.line, self.column)


class LexerError(Exception):
    """Exception raised for errors during lexical analysis."""
    
    def __init__(self, message: str, line: int, column: int, file: Optional[str] = None):
        """
        Initialize a new lexer error.
        
        Args:
            message: Error message
            line: Line number where the error occurred
            column: Column number where the error occurred
            file: Optional source file name
        """
        self.line = line
        self.column = column
        self.file = file
        
        position = f"{line}:{column}"
        if file:
            position = f"{file}:{position}"
        
        super().__init__(f"{message} at {position}")


class Lexer:
    """
    Tokenizes DOOP source code.
    
    The lexer reads the input character by character and groups characters into tokens
    according to the DOOP language syntax rules. It skips whitespace and comments,
    and provides a stream of tokens to the parser.
    """
    
    # Keywords in the DOOP language
    KEYWORDS = {
        'component': TokenType.COMPONENT,
        'view': TokenType.VIEW,
        'description': TokenType.DESCRIPTION,
        'properties': TokenType.PROPERTIES,
        'methods': TokenType.METHODS,
        'relationships': TokenType.RELATIONSHIPS,
        'visualization': TokenType.VISUALIZATION,
        'sequence': TokenType.SEQUENCE,
        'focus': TokenType.FOCUS,
        'includes': TokenType.INCLUDES,
        'default': TokenType.DEFAULT,
        'required': TokenType.REQUIRED,
        'reason': TokenType.REASON,
        'returns': TokenType.RETURNS,
        'precondition': TokenType.PRECONDITION,
        'postcondition': TokenType.POSTCONDITION,
        'color': TokenType.COLOR,
        'icon': TokenType.ICON,
        'group': TokenType.GROUP,
        'order': TokenType.ORDER,
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN
    }
    
    def __init__(self, text: str, filename: Optional[str] = None):
        """
        Initialize a new lexer with the input text.
        
        Args:
            text: The input source code
            filename: Optional source file name for error reporting
        """
        self.text = text
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if text else None
        self.tokens: List[Token] = []
        # This helps correct line counting for multiline inputs
        if text:
            i = 0
            while i < len(text) and text[i].isspace():
                if text[i] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                i += 1
                
            if i < len(text):
                self.pos = i
                self.current_char = text[i]
            else:
                self.current_char = None
        
    def error(self, message: str) -> None:
        """
        Raise a lexer error with the current position.
        
        Args:
            message: Error message
            
        Raises:
            LexerError: Always raised with the provided message and current position
        """
        raise LexerError(message, self.line, self.column, self.filename)
    
    def advance(self) -> None:
        """
        Advance to the next character in the input.
        
        Updates the current character, position, line, and column.
        """
        # Update position 
        self.pos += 1
        
        # Update column
        if self.current_char == '\n':
            self.line += 1
            self.column = 1  # Reset column to 1 for new line
        else:
            self.column += 1
        
        # Update current character
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """
        Look ahead at a character without advancing.
        
        Args:
            offset: How many characters ahead to look (default: 1)
            
        Returns:
            The character at the offset position, or None if beyond the input
        """
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            # FIXED: Don't handle newlines here since advance() already does it
            self.advance()
    
    def skip_comment(self) -> None:
        """Skip a single-line or multi-line comment."""
        # Single-line comment (// ... \n)
        if self.current_char == '/' and self.peek() == '/':
            # Skip the two slashes
            self.advance()
            self.advance()
            
            # Skip until the end of the line or end of file
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
                
            # Skip the newline if present
            if self.current_char == '\n':
                self.advance()
                
        # Multi-line comment (/* ... */)
        elif self.current_char == '/' and self.peek() == '*':
            # Skip the /* characters
            self.advance()
            self.advance()
            
            # Skip until we find the closing */
            while True:
                if self.current_char is None:
                    self.error("Unclosed multi-line comment")
                    
                if self.current_char == '*' and self.peek() == '/':
                    # Skip the closing */
                    self.advance()
                    self.advance()
                    break
                    
                self.advance()
    
    def identifier(self) -> Token:
        """
        Process an identifier or keyword.
        
        Returns:
            A TOKEN.IDENTIFIER or a keyword token
        """
        # Record the starting position for the token
        start_line = self.line
        start_column = self.column
        
        # Build the identifier string
        result = ''
        while (self.current_char is not None and 
              (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(result, TokenType.IDENTIFIER)
        
        # Create the token
        return Token(token_type, result, start_line, start_column, self.filename)
    
    def number(self) -> Token:
        """
        Process a number literal.
        
        Returns:
            A TOKEN.NUMBER token
        """
        # Record the starting position for the token
        start_line = self.line
        start_column = self.column
        
        # Build the number string
        result = ''
        has_decimal = False
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if has_decimal:
                    self.error("Invalid number format: multiple decimal points")
                has_decimal = True
            
            result += self.current_char
            self.advance()
        
        # Create the token
        return Token(TokenType.NUMBER, result, start_line, start_column, self.filename)
    
    def string(self) -> Token:
        """
        Process a string literal.
        
        Returns:
            A TOKEN.STRING token
        """
        # Record the starting position for the token
        start_line = self.line
        start_column = self.column
        
        # Skip the opening quote
        self.advance()
        
        # Build the string
        result = ''
        while self.current_char is not None and self.current_char != '"':
            # Handle escape sequences
            if self.current_char == '\\':
                self.advance()
                if self.current_char is None:
                    self.error("Unexpected end of input in string literal")
                
                # Handle escape sequences
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == 'r':
                    result += '\r'
                elif self.current_char == '\\':
                    result += '\\'
                elif self.current_char == '"':
                    result += '"'
                else:
                    self.error(f"Invalid escape sequence: \\{self.current_char}")
            else:
                result += self.current_char
            
            self.advance()
        
        # Check if we ended due to EOF (unclosed string)
        if self.current_char is None:
            self.error("Unclosed string literal")
        
        # Skip the closing quote
        self.advance()
        
        # Create the token
        return Token(TokenType.STRING, result, start_line, start_column, self.filename)
    
    def hex_color(self) -> Token:
        """
        Process a hex color literal (e.g., #FF00FF).
        
        Returns:
            A TOKEN.HEX_COLOR token
        """
        # Record the starting position for the token
        start_line = self.line
        start_column = self.column
        
        # Skip the #
        result = '#'
        self.advance()
        
        # Build the hex color string
        for _ in range(6):  # Expect exactly 6 hex digits for full color
            if self.current_char is None or not self.current_char.isalnum():
                break
            
            if not (self.current_char.isdigit() or 
                   'a' <= self.current_char.lower() <= 'f'):
                self.error(f"Invalid hex digit: {self.current_char}")
            
            result += self.current_char
            self.advance()
        
        # Allow 3-digit hex colors (#RGB -> #RRGGBB)
        if len(result) == 4:  # Including the '#'
            # It's a #RGB format, convert to #RRGGBB
            r, g, b = result[1], result[2], result[3]
            result = f"#{r}{r}{g}{g}{b}{b}"
        elif len(result) != 7:  # Not #RRGGBB
            self.error(f"Invalid hex color format: {result}")
        
        # Create the token
        return Token(TokenType.HEX_COLOR, result, start_line, start_column, self.filename)
    
    def get_next_token(self) -> Token:
        """
        Get the next token from the input.
        
        Returns:
            The next token
            
        Raises:
            LexerError: If an invalid character or syntax is encountered
        """
        while self.current_char is not None:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Skip comments
            if self.current_char == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue
            
            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            # Numbers
            if self.current_char.isdigit():
                return self.number()
            
            # Strings
            if self.current_char == '"':
                return self.string()
            
            # Hex colors
            if self.current_char == '#':
                return self.hex_color()
            
            # Symbols (single character)
            start_line = self.line
            start_column = self.column
            
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', start_line, start_column, self.filename)
            
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', start_line, start_column, self.filename)
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', start_line, start_column, self.filename)
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', start_line, start_column, self.filename)
            
            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON, ':', start_line, start_column, self.filename)
            
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', start_line, start_column, self.filename)
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', start_line, start_column, self.filename)
            
            if self.current_char == '@':
                self.advance()
                return Token(TokenType.AT, '@', start_line, start_column, self.filename)
            
            if self.current_char == '-' and self.peek() == '>':
                self.advance()  # Skip '-'
                self.advance()  # Skip '>'
                return Token(TokenType.ARROW, '->', start_line, start_column, self.filename)
            
            if self.current_char == '-':
                start_line = self.line
                start_column = self.column
                self.advance()
                return Token(TokenType.IDENTIFIER, '-', start_line, start_column, self.filename)
            
            self.error(f"Invalid character: '{self.current_char}'")

        return Token(TokenType.EOF, '', self.line, self.column, self.filename)
        
    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire input and return all tokens.
        
        Returns:
            List of all tokens in the input
            
        Raises:
            LexerError: If an invalid character or syntax is encountered
        """
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens