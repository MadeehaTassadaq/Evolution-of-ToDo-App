# Composer Tools Reference

## Overview

Composer tools add mode-switching buttons in the chat input area, allowing users to change the AI's behavior or focus.

## Frontend Configuration

```typescript
const TOOL_CHOICES = [
  {
    id: "event_finder",
    label: "Event finder",
    icon: "calendar",
    placeholderOverride: "Anything happening this weekend?",
    persistent: true,
  },
  {
    id: "puzzle",
    label: "Coffee break puzzle",
    shortLabel: "Puzzle",
    icon: "atom",
    placeholderOverride: "Give me a puzzle to solve",
    persistent: true,
  },
];

const chatkit = useChatKit({
  composer: {
    tools: TOOL_CHOICES,
    placeholder: "Ask me anything...",
  },
});
```

## Backend Handling

```python
async def respond(self, thread, item, context):
    tool_choice = context.get("tool_choice")

    if tool_choice == "event_finder":
        agent = self.event_finder_agent
    elif tool_choice == "puzzle":
        agent = self.puzzle_agent
    else:
        agent = self.general_agent

    result = Runner.run_streamed(agent, input_items, context=agent_context)
    async for event in stream_agent_response(agent_context, result):
        yield event
```
