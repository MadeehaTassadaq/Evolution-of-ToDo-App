import os
from typing import Dict, Any, List
from openai import OpenAI
from pydantic import BaseModel


class TodoAgent:
    """
    Agent class that integrates with OpenAI to handle todo management tasks.
    Uses MCP tools to perform actual operations on the todo list.
    """

    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Define the system prompt for the todo agent
        self.system_prompt = """
        You are a helpful todo management assistant. Your job is to help users manage their tasks through natural language.

        You can help with:
        - Adding new tasks
        - Listing existing tasks
        - Updating task details
        - Marking tasks as completed
        - Deleting tasks

        When a user requests an action, you should use the appropriate tools to perform the action.
        Always confirm with the user when performing destructive actions like deleting tasks.
        If you're unsure about any details, ask the user for clarification.
        Be friendly and concise in your responses.
        """

    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process a user message and return an appropriate response.

        Args:
            user_message: The message from the user
            conversation_history: Previous messages in the conversation
            user_id: The ID of the user

        Returns:
            Dictionary containing the agent's response and any tool calls made
        """
        try:
            # Prepare messages for the OpenAI API
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add conversation history
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "assistant"),
                    "content": msg.get("content", "")
                })

            # Add the current user message
            messages.append({"role": "user", "content": user_message})

            # Define available tools
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "description": "Add a new task to the user's todo list",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "The ID of the user"},
                                "title": {"type": "string", "description": "The title of the task"},
                                "description": {"type": "string", "description": "Optional description of the task"},
                                "due_date": {"type": "string", "description": "Optional due date in ISO format"}
                            },
                            "required": ["user_id", "title"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "List tasks for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "The ID of the user"},
                                "status_filter": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter tasks by status"}
                            },
                            "required": ["user_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_task",
                        "description": "Update an existing task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "The ID of the user"},
                                "task_id": {"type": "integer", "description": "The ID of the task to update"},
                                "title": {"type": "string", "description": "New title for the task"},
                                "description": {"type": "string", "description": "New description for the task"},
                                "status": {"type": "string", "enum": ["pending", "completed"], "description": "New status for the task"},
                                "due_date": {"type": "string", "description": "New due date in ISO format"}
                            },
                            "required": ["user_id", "task_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_task",
                        "description": "Mark a task as completed",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "The ID of the user"},
                                "task_id": {"type": "integer", "description": "The ID of the task to complete"}
                            },
                            "required": ["user_id", "task_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_task",
                        "description": "Delete a task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "The ID of the user"},
                                "task_id": {"type": "integer", "description": "The ID of the task to delete"}
                            },
                            "required": ["user_id", "task_id"]
                        }
                    }
                }
            ]

            # Call the OpenAI API with tools
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can change this to gpt-4 if preferred
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=1000
            )

            # Extract the response
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Prepare the result
            result = {
                "response": response_message.content or "",
                "tool_calls": [],
                "success": True
            }

            # Process any tool calls
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = eval(tool_call.function.arguments)  # Note: In production, use json.loads safely

                    # Add user_id to function args if not present
                    if "user_id" not in function_args:
                        function_args["user_id"] = user_id

                    # Add the tool call to our result
                    result["tool_calls"].append({
                        "name": function_name,
                        "arguments": function_args
                    })

            return result

        except Exception as e:
            return {
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "tool_calls": [],
                "success": False,
                "error": str(e)
            }

    def format_tasks_for_response(self, tasks: List[Dict[str, Any]]) -> str:
        """
        Format a list of tasks into a human-readable string for the agent response.

        Args:
            tasks: List of task dictionaries

        Returns:
            Formatted string representation of tasks
        """
        if not tasks:
            return "You don't have any tasks."

        formatted_tasks = []
        for task in tasks:
            status_icon = "✅" if task.get("status") == "completed" else "📝"
            task_str = f"{status_icon} [{task.get('id')}] {task.get('title')}"
            if task.get('description'):
                task_str += f": {task.get('description')}"
            if task.get('due_date'):
                task_str += f" (Due: {task.get('due_date')})"
            formatted_tasks.append(task_str)

        return "\n".join(formatted_tasks)