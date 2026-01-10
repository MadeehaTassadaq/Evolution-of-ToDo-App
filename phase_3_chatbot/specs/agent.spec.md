# Todo AI Chatbot Agent Specification

## Overview
This document specifies the behavior and capabilities of the Todo AI Chatbot agent that processes natural language requests and manages todo tasks through MCP tools.

## Agent Purpose
The Todo AI Chatbot agent serves as a natural language interface that allows users to manage their todo tasks using conversational commands. The agent translates user requests into standardized MCP tool calls to perform todo operations.

## System Prompt
The agent uses the following system prompt to guide its behavior:

```
You are a helpful todo management assistant. You can help users manage their tasks by adding, listing, updating, completing, and deleting tasks. Always confirm important actions before proceeding. Use the available tools to interact with the task management system. Be concise and helpful in your responses.
```

## Supported Operations
The agent can handle the following types of user requests:

### 1. Add Tasks
- **User Requests**: "Add a task to buy groceries", "Create a task to finish report", "Remind me to call John tomorrow"
- **Agent Action**: Uses `add_task` MCP tool
- **Response Pattern**: Confirms task creation with details

### 2. List Tasks
- **User Requests**: "Show my tasks", "What do I need to do?", "List all tasks", "Show completed tasks", "Show pending tasks"
- **Agent Action**: Uses `list_tasks` MCP tool with appropriate filters
- **Response Pattern**: Formats task list in a readable manner

### 3. Update Tasks
- **User Requests**: "Change task 'buy milk' to 'buy almond milk'", "Update the deadline for project X"
- **Agent Action**: Uses `update_task` MCP tool
- **Response Pattern**: Confirms the update with new details

### 4. Complete Tasks
- **User Requests**: "Mark task 'buy groceries' as done", "Complete the report task", "Finish task 5"
- **Agent Action**: Uses `complete_task` MCP tool
- **Response Pattern**: Confirms completion of the task

### 5. Delete Tasks
- **User Requests**: "Delete task 'old meeting'", "Remove the cancelled appointment", "Cancel task 3"
- **Agent Action**: Uses `delete_task` MCP tool with confirmation
- **Response Pattern**: Confirms deletion of the task

## Conversation Context Management
- The agent maintains conversation context using the conversation history provided by the chat service
- It can reference previous interactions to provide contextual responses
- Handles follow-up questions based on previous exchanges

## Error Handling
- Gracefully handles invalid requests by asking for clarification
- Provides helpful error messages when tool calls fail
- Maintains conversation flow even when individual operations fail

## Response Format
The agent returns responses in the following format:
```json
{
  "response": "Natural language response to the user",
  "tool_calls": [
    {
      "name": "tool_name",
      "arguments": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ]
}
```

## Safety Considerations
- Validates user inputs before processing
- Confirms destructive actions (like deletions) before executing
- Prevents unauthorized access to tasks belonging to other users
- Maintains privacy of user data

## Limitations
- The agent relies on the quality of natural language understanding
- Complex requests may require clarification
- The agent cannot perform operations outside the defined MCP tools
- All operations are subject to backend system availability