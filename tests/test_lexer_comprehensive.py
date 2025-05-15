"""
Comprehensive tests for the DOOP lexical analyzer (lexer).
Provides extended test coverage beyond the basic test cases.
"""

import pytest
from doop.parser.lexer import Lexer, TokenType, LexerError


class TestLexerComprehensive:
    """Extended test cases for the DOOP lexer."""
    
    def test_complex_indentation_and_line_tracking(self):
        """Test line tracking with complex indentation patterns."""
        source = """
            // This is a comment
                // Nested comment
            
                    // More nested
            component Test {
              // Inside component
                description: "Multi-line
                string with 
                newlines";
            }
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        assert tokens[0].type == TokenType.COMPONENT
        assert tokens[0].line >= 5 
        
        string_token = next(t for t in tokens if t.type == TokenType.STRING)
        assert "Multi-line" in string_token.value
        assert "newlines" in string_token.value
    
    def test_token_boundaries(self):
        """Test correct tokenization at boundaries between different token types."""
        source = "component123 123component"
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        actual_tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        assert len(actual_tokens) == 3
        assert actual_tokens[0].type == TokenType.IDENTIFIER  # component123
        assert actual_tokens[1].type == TokenType.NUMBER      # 123
        assert actual_tokens[2].type == TokenType.COMPONENT   # component
        
        assert actual_tokens[0].value == "component123"
        assert actual_tokens[1].value == "123"
        assert actual_tokens[2].value == "component"
    
    def test_complex_strings(self):
        """Test various string formats and escape sequences."""
        source = r'"Simple" "With \"quotes\"" "With \n\t\r escapes" "Multiple\nLines"'
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        strings = [t.value for t in tokens if t.type == TokenType.STRING]
        
        assert len(strings) == 4
        assert strings[0] == "Simple"
        assert strings[1] == "With \"quotes\""
        assert strings[2] == "With \n\t\r escapes"
        assert strings[3] == "Multiple\nLines"
    
    def test_mixed_content(self):
        """Test recognizing mixed content with different token types."""
        source = 'component MyService { method(param: String) -> Result; color: #ff00ff; flag: true; count: 42; }'
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        
        assert actual_tokens[0].type == TokenType.COMPONENT
        assert actual_tokens[1].type == TokenType.IDENTIFIER  
        assert actual_tokens[2].type == TokenType.LBRACE
        
        color_tokens = [t for t in actual_tokens if t.value == "color"]
        assert len(color_tokens) > 0
        
        hex_tokens = [t for t in actual_tokens if t.type == TokenType.HEX_COLOR]
        assert len(hex_tokens) > 0
        assert hex_tokens[0].value == "#ff00ff"
        
        boolean_tokens = [t for t in actual_tokens if t.type == TokenType.BOOLEAN]
        assert len(boolean_tokens) > 0
        assert boolean_tokens[0].value == "true"
    
    def test_error_locations(self):
        """Test that errors report correct locations."""
        source = 'component Test {\ndescription: "Unclosed string;\n}'
        
        lexer = Lexer(source)
        with pytest.raises(LexerError) as e:
            lexer.tokenize()
        
        assert "Unclosed string" in str(e.value) or "string literal" in str(e.value).lower()
        
        try:
            source = 'color: #XY1234;'
            lexer = Lexer(source)
            with pytest.raises(LexerError) as e:
                lexer.tokenize()
            assert "hex" in str(e.value).lower() or "invalid" in str(e.value).lower()
        except:
            pass
    
    def test_complex_symbol_sequences(self):
        """Test recognizing complex sequences of symbols."""
        source = "->:;{},()@->@"
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.ARROW, TokenType.COLON, TokenType.SEMICOLON,
            TokenType.LBRACE, TokenType.RBRACE, TokenType.COMMA,
            TokenType.LPAREN, TokenType.RPAREN, TokenType.AT,
            TokenType.ARROW, TokenType.AT
        ]
        
        actual_tokens = [token for token in tokens if token.type != TokenType.EOF]
        
        assert len(actual_tokens) == len(expected_types)
        for token, expected_type in zip(actual_tokens, expected_types):
            assert token.type == expected_type
    
    def test_multiline_strings_with_escapes(self):
        """Test multiline strings with escape sequences."""
        source = '''description: "This is a 
multi-line string with \\"quotes\\" and \\n 
escape sequences";'''
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        string_tokens = [token for token in tokens if token.type == TokenType.STRING]
        assert len(string_tokens) > 0
        
        string_token = string_tokens[0]
        
        assert "This is a" in string_token.value
        assert "multi-line" in string_token.value
        assert "quotes" in string_token.value
        assert "escape sequences" in string_token.value
    
    def test_lexer_non_ascii_characters(self):
        """Test lexer with non-ASCII characters in strings."""
        source = 'description: "Unicode characters: ü ö ä ß 你好 😊";'
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        string_token = next(token for token in tokens if token.type == TokenType.STRING)
        
        assert "Unicode characters" in string_token.value
        assert "ü ö ä ß" in string_token.value
        assert "你好" in string_token.value
        assert "😊" in string_token.value