"""
Complete Server Action Handler Pattern

This file shows the complete pattern for handling server-side widget actions in ChatKit.
"""

from typing import Any, AsyncIterator
from chatkit.server import ChatKitServer
from chatkit.types import (
    Action, WidgetItem, ThreadItemReplacedEvent,
    ThreadItemDoneEvent, AssistantMessageItem, ClientEffectEvent,
    ThreadMetadata, ThreadStreamEvent
)

class ExampleChatKitServer(ChatKitServer[dict]):

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Handle server-side widget actions."""

        if action.type == "line.select":
            line_id = action.payload["id"]

            # 1. Update widget with selection
            updated_widget = build_line_selector_widget(
                lines=self.lines,
                selected=line_id,
            )
            yield ThreadItemReplacedEvent(
                item=sender.model_copy(update={"widget": updated_widget})
            )

            # 2. Send assistant message
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("msg", thread, context),
                    created_at=datetime.now(),
                    content=[{"text": f"Selected {line_id}"}],
                )
            )

            # 3. Trigger client effect
            yield ClientEffectEvent(
                name="location_select_mode",
                data={"lineId": line_id},
            )
