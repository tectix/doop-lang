# DOOP: Document-Oriented Object Programming

DOOP is a programming language designed to unify documentation, object-oriented design, and diagram generation in a single cohesive system. It enables developers to create self-documenting system architectures with automatic visualization.

## Features

- Living Documentation - Code and documentation are always in sync
- Visual Understanding - Automatic diagram generation based on code structure
- Relationship Clarity - Explicit modeling of dependencies and interactions
- Type System - Strong typing for properties and methods
- Security-First Design - Built with security best practices from the ground up
- Integration Friendly - Works alongside existing tech stacks

## Example

component UserService {
  description: "Service for managing users";
  
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

## Installation

# Install from PyPI
pip install doop-lang

# Or install from source
git clone https://github.com/yourusername/doop-lang.git
cd doop-lang
pip install -e .

### Requirements

- Python 3.8+
- Graphviz (for diagram generation)

## Usage

### Create a New Project

doop init my_project
cd my_project

### Edit DOOP Files

Edit the example file in src/example.doop or create your own files.

### Compile

doop compile src/*.doop -o output

### View Results

The output directory will contain:
- docs/ - Markdown documentation
- diagrams/ - SVG/PNG diagrams

## Documentation

- User Guide (docs/user_guide.md)
- Language Specification (docs/language_spec.md)
- Examples (docs/examples/)
  - Hello World (docs/examples/hello_world.doop)
  - Microservice Architecture (docs/examples/microservice_architecture.doop)

## Security Features

DOOP was designed with security as a priority:

- Secure File Handling - Path validation prevents directory traversal
- Resource Limits - Protection against resource exhaustion attacks
- Safe Command Execution - Prevents command injection in diagram generation
- Dependency Verification - Validates and verifies dependencies
- Input Validation - All inputs are validated before processing

## Development Workflow

1. Clone the repository
   git clone https://github.com/yourusername/doop-lang.git
   cd doop-lang

2. Set up a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install development dependencies
   pip install -e ".[dev]"

4. Run tests
   pytest

5. Check code style
   black --check src tests

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create your feature branch (git checkout -b feature/your-feature)
3. Commit your changes (git commit -m 'Add some feature')
4. Push to the branch (git push origin feature/your-feature)
5. Open a Pull Request

Please ensure your code passes all tests and follows the project's coding style.

## Issues and Feature Requests

Use the GitHub issue tracker to report bugs or suggest features.

## Roadmap

- IDE Integration - VS Code extensions and syntax highlighting
- Interactive Visualization - Browser-based interactive diagrams
- Schema Validation - JSON Schema generation from DOOP types
- Code Generation - Generate scaffolding code from DOOP definitions