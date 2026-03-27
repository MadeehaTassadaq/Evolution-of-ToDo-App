# Entity Tagging (@mentions) Reference

## Overview

Entity tagging enables users to @mention entities (users, articles, tasks) directly in the chat composer.

## Frontend Configuration

```typescript
import { useChatKit, type Entity } from "@openai/chatkit-react";

const chatkit = useChatKit({
  entities: {
    onTagSearch: async (query: string): Promise<Entity[]> => {
      const results = await searchEntities(query);
      return results.map(item => ({
        id: item.id,
        title: item.name,
        icon: item.type === "person" ? "profile" : "document",
        group: item.type === "People" ? "People" : "Articles",
        interactive: true,
        data: { type: item.type, url: item.url },
      }));
    },
    onClick: (entity: Entity) => {
      if (entity.data?.url) navigate(entity.data.url);
    },
  },
});
```

## Backend Conversion

Convert entity tags to model-readable markers:

```python
class EntityAwareConverter:
    def _entity_to_marker(self, entity: EntityTag) -> str:
        if entity.data.get("type") == "article":
            return f"<ARTICLE_REFERENCE id='{entity.id}'>{entity.title}</ARTICLE_REFERENCE>"
        if entity.data.get("type") == "user":
            return f"<USER_REFERENCE id='{entity.id}'>{entity.title}</USER_REFERENCE>"
        return f"<ENTITY id='{entity.id}'>{entity.title}</ENTITY>"
```
