# CodeComprehender

A tool for generating comprehensive code documentation using LLM and architecture graph

## Features
- Generates detailed Javadoc comments for classes, methods, and fields
- Generates the Architecture graph (AST graph + call graph)

## Configuration

The tool uses environment variables for configuration. Create a `.env` file in the project root with the following:

### Azure OpenAI Configuration
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT`: Your model deployment name
- `AZURE_OPENAI_API_VERSION`: API version 
- `AZURE_OPENAI_TEMPERATURE`: Temperature for generation (0.0-1.0)

## Pre-requirement
* uv
* python > 3.11
* Antlr (brew install antlr)
* graphviz (brew install graphviz)

## Usage

### Generate Antlr parse 
```bash
bash script/generate_parser.sh
```

### Generate documentation for code

```bash
# Don't apply change on the existing project copy it and override existing comment
uv run python -m src.cli document "/path/to/java/" --copy --output-dir . --existing override

# Don't apply change on the existing project copy it and keep both existing and generated comment
uv run python -m src.cli document "/path/to/java/" --copy --output-dir . --existing keep-both


# Don't apply change on the existing project copy it and skip generated comment if there is existing one
uv run python -m src.cli document "/path/to/java/" --copy --output-dir . --existing skip



# Apply change on the existing project and skip generated comment if there is existing one
uv run python -m src.cli document "/path/to/java/"  --output-dir . --existing skip

```

##### Output Example

Input Java class:
```java
public class User {
    private String username;
    private String email;

    public User(String username, String email) {
        this.username = username;
        this.email = email;
    }
}
```

Generated documentation:
```java
/**
 * Represents a user in the system with basic identification information.
 * 
 * @author Your Name
 * @since 1.0.0
 */
public class User {
    /**
     * The unique username of the user.
     * Must be non-null and unique within the system.
     */
    private String username;

    /**
     * The email address associated with the user.
     * Used for communication and account verification.
     */
    private String email;

    /**
     * Creates a new User with the specified username and email.
     * 
     * @param username The unique identifier for the user
     * @param email The user's email address
     * @throws IllegalArgumentException if username or email is null
     */
    public User(String username, String email) {
        this.username = username;
        this.email = email;
    }
}
```
### Generate architecture graph
```bash
uv run python -m src.cli architecture "path/to/java/project" -o ./output
```
##### Output example
Call Graph
![Call Graph](doc/img/call_graph.jpg)

Abstract Syntax Tree 
![AST Graph](doc/img/ast.jpg) 
