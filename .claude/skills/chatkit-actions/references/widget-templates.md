# Widget Templates Reference

## Overview

Widget templates (`.widget` files) define reusable, data-driven UI components that can be rendered in chat responses.

## Component Reference

### ListView
```json
{
  "type": "ListView",
  "children": [ ... ListViewItem components ... ]
}
```

### ListViewItem
```json
{
  "type": "ListViewItem",
  "key": "unique-key",
  "gap": 3,
  "onClickAction": {
    "type": "action.type",
    "handler": "client" | "server",
    "payload": { ... }
  },
  "children": [ ... ]
}
```

### Row
```json
{
  "type": "Row",
  "gap": 3,
  "align": "center" | "start" | "end" | "stretch",
  "justify": "start" | "end" | "center" | "between" | "around",
  "children": [ ... ]
}
```

### Button
```json
{
  "type": "Button",
  "label": "Click me",
  "variant": "solid" | "outline" | "ghost",
  "color": "discovery" | "warning" | "success",
  "size": "sm" | "md" | "lg",
  "pill": true,
  "onClickAction": {
    "type": "action.type",
    "handler": "client",
    "payload": { ... }
  }
}
```

## Python Usage

```python
from chatkit.widgets import WidgetTemplate

# Load template
template = WidgetTemplate.from_file("my_widget.widget")

# Build with data
widget = template.build(data={"items": [...]})

# Yield as widget item
yield ThreadItemDoneEvent(item=WidgetItem(..., widget=widget))
```
