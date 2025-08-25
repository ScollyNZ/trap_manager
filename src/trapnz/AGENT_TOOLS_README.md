# Trap.NZ Agent Tools

This module provides OpenAI-ready agent tools for interacting with Trap.NZ trap data. These tools enable AI agents to query trap lines, traps, and records through natural language.

## 🚀 Quick Start

```python
from trapnz import TrapNZDatabase, create_agent_tools

# Initialize your database
db = TrapNZDatabase()

# Create agent tools
agent_tools = create_agent_tools(db)

# Get tool schemas for OpenAI
schemas = agent_tools.get_tool_schemas()

# Get tool functions
functions = agent_tools.get_tool_functions()
```

## 🛠️ Available Tools

### Basic Data Retrieval

#### `get_all_lines()`
Retrieves all trap lines from the database.
- **Parameters**: None
- **Returns**: List of all lines with projects, tags, and metadata

#### `get_all_traps()`
Retrieves all traps from the database.
- **Parameters**: None
- **Returns**: List of all traps with health status and performance metrics

#### `get_all_trap_records()`
Retrieves the latest record for each trap.
- **Parameters**: None
- **Returns**: List of latest trap records with sensor data

### Specific Data Retrieval

#### `get_lines_by_uuids(line_uuids: List[str])`
Retrieves specific lines by their UUIDs.
- **Parameters**: 
  - `line_uuids`: List of line UUID strings
- **Returns**: Detailed information about requested lines

#### `get_traps_by_line_uuids(line_uuids: List[str])`
Retrieves all traps within specific lines.
- **Parameters**:
  - `line_uuids`: List of line UUID strings
- **Returns**: Traps with health status and performance metrics

#### `get_latest_records_for_traps(trap_uuids: List[str])`
Retrieves latest records for specific traps.
- **Parameters**:
  - `trap_uuids`: List of trap UUID strings
- **Returns**: Latest sensor data and status for each trap

#### `get_trap_records_by_trap(trap_uuid: str, limit: int = 100)`
Retrieves multiple records for a specific trap.
- **Parameters**:
  - `trap_uuid`: Trap UUID string
  - `limit`: Maximum number of records (default: 100)
- **Returns**: Historical records ordered by date

### Search and Analysis

#### `search_traps_by_status(status: str)`
Searches for traps by health status.
- **Parameters**:
  - `status`: Health status ("green", "amber", "red", "unknown")
- **Returns**: Traps matching the status criteria

#### `search_traps_by_type(trap_type: str)`
Searches for traps by type.
- **Parameters**:
  - `trap_type`: Trap type (e.g., "DOC200", "DOC250")
- **Returns**: All traps of the specified type

#### `get_trap_performance_summary(trap_uuid: str)`
Gets performance summary for a specific trap.
- **Parameters**:
  - `trap_uuid`: Trap UUID string
- **Returns**: Performance metrics, catch rates, and battery health

#### `get_line_summary(line_uuid: str)`
Gets summary for a specific line.
- **Parameters**:
  - `line_uuid`: Line UUID string
- **Returns**: Line statistics, trap count, and overall health

## 🤖 OpenAI Integration

### Function Calling Setup

```python
from openai import OpenAI
from trapnz import TrapNZDatabase, create_agent_tools

# Initialize
db = TrapNZDatabase()
agent_tools = create_agent_tools(db)

# Get schemas and functions
tool_schemas = agent_tools.get_tool_schemas()
tool_functions = agent_tools.get_tool_functions()

# Use with OpenAI
client = OpenAI(api_key="your-api-key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "How many traps do I have?"}],
    tools=tool_schemas,
    tool_choice="auto"
)
```

### Example Queries

Users can ask natural language questions like:

- "How many trap lines do I have?"
- "Show me all traps with red health status"
- "What's the performance summary for trap abc-123?"
- "How many DOC200 traps do I have?"
- "Give me a summary of line xyz-789"
- "What are the latest records for all my traps?"
- "Find all traps with low battery voltage"
- "Show me traps that haven't been checked recently"

## 📊 Response Format

All tools return responses in a consistent format:

```python
{
    "success": True,
    "data": {
        # Tool-specific data structure
    }
}
```

### Error Handling

```python
{
    "success": False,
    "error": "Error description"
}
```

## 🔧 Standalone Usage

You can also use the tools directly without OpenAI:

```python
from trapnz import TrapNZDatabase, create_agent_tools

db = TrapNZDatabase()
tools = create_agent_tools(db)

# Get all lines
result = tools.get_all_lines()
print(f"Total lines: {result['data']['total_lines']}")

# Search traps by status
red_traps = tools.search_traps_by_status("red")
print(f"Red status traps: {red_traps['data']['total_traps']}")

# Get trap performance
performance = tools.get_trap_performance_summary("trap-uuid")
print(f"Total possums: {performance['data']['performance_metrics']['total_possums']}")
```

## 🧪 Testing with TEST_MODE

When `TEST_MODE=true` is set in your `.env` file, the tools will work with canned test data instead of real API calls:

```bash
# .env
TEST_MODE=true
```

This is perfect for:
- Development and testing
- Unit testing the agent tools
- Demonstrations without real data
- Offline development

## 📁 File Structure

```
src/trapnz/
├── agent_tools.py          # Main agent tools implementation
├── agent_example.py        # OpenAI integration examples
├── database.py             # Database operations
├── models.py               # Pydantic data models
└── logging_config.py       # Logging configuration
```

## 🚀 Advanced Usage

### Custom Tool Wrapping

```python
class CustomTrapTools(TrapNZAgentTools):
    def custom_analysis(self, trap_uuid: str) -> Dict[str, Any]:
        """Custom analysis tool"""
        # Your custom logic here
        pass

# Use custom tools
custom_tools = CustomTrapTools(db)
```

### Batch Operations

```python
# Process multiple traps efficiently
trap_uuids = ["uuid1", "uuid2", "uuid3"]
results = []

for uuid in trap_uuids:
    summary = agent_tools.get_trap_performance_summary(uuid)
    if summary["success"]:
        results.append(summary["data"])
```

## 🔒 Security Considerations

- All tools are read-only by default
- Input validation is performed on UUIDs
- Error messages don't expose sensitive information
- Database connections are properly managed

## 📈 Performance Tips

- Use specific UUID queries when possible
- Leverage the built-in caching (1-hour API limit)
- Batch related queries together
- Use database-only methods for fast local access

## 🤝 Contributing

To add new tools:

1. Add the tool method to `TrapNZAgentTools`
2. Add the schema to `get_tool_schemas()`
3. Add the function to `get_tool_functions()`
4. Update this documentation
5. Add tests

## 📞 Support

For questions or issues:
- Check the examples in `agent_example.py`
- Review the test files for usage patterns
- Ensure your database is properly initialized
- Verify TEST_MODE configuration if using test data
