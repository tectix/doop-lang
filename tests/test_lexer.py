"""
Tests for the DOOP lexical analyzer (lexer).
"""

import pytest
from doop.parser.lexer import Lexer, TokenType, LexerError


class TestLexer:
    """Test cases for the DOOP lexer."""
    
    def test_empty_input(self):
        """Test tokenizing an empty input."""
        lexer = Lexer("")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_keywords(self):
        """Test recognizing all keywords."""
        source = """
        component view description properties methods
        relationships visualization sequence focus includes
        default required reason returns precondition postcondition
        color icon group order true false
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_keywords = [
            TokenType.COMPONENT, TokenType.VIEW, TokenType.DESCRIPTION, 
            TokenType.PROPERTIES, TokenType.METHODS, TokenType.RELATIONSHIPS,
            TokenType.VISUALIZATION, TokenType.SEQUENCE, TokenType.FOCUS,
            TokenType.INCLUDES, TokenType.DEFAULT, TokenType.REQUIRED,
            TokenType.REASON, TokenType.RETURNS, TokenType.PRECONDITION,
            TokenType.POSTCONDITION, TokenType.COLOR, TokenType.ICON,
            TokenType.GROUP, TokenType.ORDER, TokenType.BOOLEAN, TokenType.BOOLEAN
        ]
        
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        
        assert len(actual_tokens) == len(expected_keywords)
        for token, expected_type in zip(actual_tokens, expected_keywords):
            assert token.type == expected_type
    
    def test_symbols(self):
        """Test recognizing all symbols."""
        source = "{ } ( ) : ; , -> @"
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_symbols = [
            TokenType.LBRACE, TokenType.RBRACE, TokenType.LPAREN, TokenType.RPAREN,
            TokenType.COLON, TokenType.SEMICOLON, TokenType.COMMA, TokenType.ARROW,
            TokenType.AT
        ]
        
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        
        assert len(actual_tokens) == len(expected_symbols)
        for token, expected_type in zip(actual_tokens, expected_symbols):
            assert token.type == expected_type
    
    def test_identifiers(self):
        """Test recognizing identifiers."""
        source = "component UserService getUserById user_id String"
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected = [
            (TokenType.COMPONENT, "component"),
            (TokenType.IDENTIFIER, "UserService"),
            (TokenType.IDENTIFIER, "getUserById"),
            (TokenType.IDENTIFIER, "user_id"),
            (TokenType.IDENTIFIER, "String"),
            (TokenType.EOF, "")
        ]
        
        assert len(tokens) == len(expected)
        for token, (expected_type, expected_value) in zip(tokens, expected):
            assert token.type == expected_type
            assert token.value == expected_value
    
    def test_string_literals(self):
        """Test recognizing string literals."""
        source = '"Simple string" "String with \\"quotes\\"" "String with \\n escape"'
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_values = [
            "Simple string",
            "String with \"quotes\"",
            "String with \n escape"
        ]
        
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        
        assert len(actual_tokens) == len(expected_values)
        for token, expected_value in zip(actual_tokens, expected_values):
            assert token.type == TokenType.STRING
            assert token.value == expected_value
    
    def test_number_literals(self):
        """Test recognizing number literals."""
        source = "42 3.14 0 -123.456"
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Expected token values (note: -123.456 will be tokenized as '-' and '123.456')
        expected_types_values = [
            (TokenType.NUMBER, "42"),
            (TokenType.NUMBER, "3.14"),
            (TokenType.NUMBER, "0"),
            (TokenType.IDENTIFIER, "-"),  # '-' is treated as an identifier since it's not part of a valid token
            (TokenType.NUMBER, "123.456"),
            (TokenType.EOF, "")
        ]
        
        # Check token types and values
        assert len(tokens) == len(expected_types_values)
        for token, (expected_type, expected_value) in zip(tokens, expected_types_values):
            assert token.type == expected_type
            assert token.value == expected_value
    
    def test_hex_color_literals(self):
        """Test recognizing hex color literals."""
        source = "#ff0000 #00ff00 #0000ff #f00 #0f0 #00f"
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_values = [
            "#ff0000", "#00ff00", "#0000ff", "#ff0000", "#00ff00", "#0000ff" 
        ]
        
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        
        assert len(actual_tokens) == len(expected_values)
        for token, expected_value in zip(actual_tokens, expected_values):
            assert token.type == TokenType.HEX_COLOR
            assert token.value == expected_value
    
    def test_comments(self):
        """Test skipping comments."""
        source = """
        // Single-line comment
        component // Another comment
        UserService /* Multi-line
        comment */ {
            // Property comment
            description: "A service"; // End of line comment
        }
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.COMPONENT,
            TokenType.IDENTIFIER,  # UserService
            TokenType.LBRACE,
            TokenType.DESCRIPTION,
            TokenType.COLON,
            TokenType.STRING,      # "A service"
            TokenType.SEMICOLON,
            TokenType.RBRACE
        ]
        
        # Filter out EOF token
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        
        # Check token types
        assert len(actual_tokens) == len(expected_types)
        for token, expected_type in zip(actual_tokens, expected_types):
            assert token.type == expected_type
    
    def test_whitespace(self):
        """Test handling of whitespace."""
        source = """
        component  UserService    {
            description:    "A service"   ;
        }
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected = [
            (TokenType.COMPONENT, "component"),
            (TokenType.IDENTIFIER, "UserService"),
            (TokenType.LBRACE, "{"),
            (TokenType.DESCRIPTION, "description"),
            (TokenType.COLON, ":"),
            (TokenType.STRING, "A service"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.RBRACE, "}")
        ]
        
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        
        assert len(actual_tokens) == len(expected)
        for token, (expected_type, expected_value) in zip(actual_tokens, expected):
            assert token.type == expected_type
            assert token.value == expected_value
    
    def test_line_column_tracking(self):
        """Test tracking of line and column numbers."""
        source = """
component UserService {
    description: "A service";
}
"""
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_lines = [2, 2, 2, 3, 3, 3, 3, 4]
        
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        
        assert len(actual_tokens) == len(expected_lines)
        for token, expected_line in zip(actual_tokens, expected_lines):
            assert token.line == expected_line
    
    def test_lexical_errors(self):
        """Test handling of lexical errors."""
        with pytest.raises(LexerError) as excinfo:
            lexer = Lexer('"Unclosed string')
            lexer.tokenize()
        assert "Unclosed string" in str(excinfo.value)
        
        with pytest.raises(LexerError) as excinfo:
            lexer = Lexer('/* Unclosed comment')
            lexer.tokenize()
        assert "Unclosed multi-line comment" in str(excinfo.value)
        
        with pytest.raises(LexerError) as excinfo:
            lexer = Lexer(r'"Invalid \z escape"')
            lexer.tokenize()
        assert "Invalid escape sequence" in str(excinfo.value)
        
        with pytest.raises(LexerError) as excinfo:
            lexer = Lexer('$invalid')
            lexer.tokenize()
        assert "Invalid character" in str(excinfo.value)
    
    def test_complex_input(self):
        """Test tokenizing a complex input."""
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
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        assert len(actual_tokens) > 50  
        
        component_token = actual_tokens[0]
        assert component_token.type == TokenType.COMPONENT
        assert component_token.value == "component"
        
        user_service_token = actual_tokens[1]
        assert user_service_token.type == TokenType.IDENTIFIER
        assert user_service_token.value == "UserService"
        
        visualization_index = next(i for i, t in enumerate(actual_tokens) if t.type == TokenType.VISUALIZATION)
        assert visualization_index > 0
        
        color_token = actual_tokens[visualization_index + 2]  
        assert color_token.type == TokenType.COLOR
        assert color_token.value == "color"
        
        hex_color_token = actual_tokens[visualization_index + 4]  
        assert hex_color_token.type == TokenType.HEX_COLOR
        assert hex_color_token.value == "#3498db"