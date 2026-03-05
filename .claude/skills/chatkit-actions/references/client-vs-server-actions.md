# Client vs Server Actions Guide

## Decision Framework

| Question | Client Action | Server Action |
|----------|--------------|---------------|
| Mutates backend data? | No | **Yes** |
| Needs widget update? | No | **Yes** |
| Navigation only? | **Yes** | No |
| Sends follow-up message? | **Yes** | No |
| Local state change? | **Yes** | No |

## Client Action Flow

```
User clicks → onAction fires → Local processing only
```

```typescript
// Frontend
onAction: async (action, widgetItem) => {
  if (action.type === "open_details") {
    navigate(`/details/${action.payload?.id}`);
  }
  if (action.type === "more") {
    await chatkit.sendUserMessage({ text: "More please" });
  }
}
```

## Server Action Flow

```
User clicks → onAction fires → sendCustomAction → Backend action() → Widget update
```

```typescript
// Frontend - forward to server
onAction: async (action, widgetItem) => {
  if (action.type === "approve") {
    await chatkit.sendCustomAction(action, widgetItem.id);
  }
}
```

```python
# Backend - handle and respond
async def action(self, thread, action, sender, context):
    if action.type == "approve":
        await self.db.approve(action.payload["id"])
        updated_widget = build_widget(approved=True)
        yield ThreadItemReplacedEvent(item=sender.model_copy(update={"widget": updated_widget}))
        yield ThreadItemDoneEvent(item=AssistantMessageItem(content=[{"text": "Approved!"}]))
```
