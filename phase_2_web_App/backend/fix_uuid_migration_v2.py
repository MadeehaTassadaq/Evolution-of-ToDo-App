"""
Improved migration script to fix VARCHAR -> UUID conversion for conversation and message tables.

This aligns the database schema with the Python models and Hackathon requirements.
"""

import os
from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

def run_migration():
    """Convert VARCHAR columns to UUID for conversation and message tables."""

    engine = create_engine(DATABASE_URL)

    print("Starting UUID migration...")
    print(f"Database: {DATABASE_URL[:50]}...")

    # Check current state
    with engine.connect() as conn:
        print("\n=== BEFORE MIGRATION ===")
        result = conn.execute(text("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name IN ('conversation', 'message')
            AND column_name IN ('id', 'user_id', 'conversation_id')
            ORDER BY table_name, ordinal_position;
        """))
        for row in result:
            print(f"{row[0]}.{row[1]}: {row[2]}")

    # Execute each migration step in a separate transaction
    steps = [
        {
            "name": "Drop message foreign key",
            "sql": "ALTER TABLE message DROP CONSTRAINT IF EXISTS message_conversation_id_fkey;"
        },
        {
            "name": "Convert conversation.id to UUID",
            "sql": "ALTER TABLE conversation ALTER COLUMN id TYPE UUID USING id::UUID;"
        },
        {
            "name": "Convert conversation.user_id to UUID",
            "sql": "ALTER TABLE conversation ALTER COLUMN user_id TYPE UUID USING user_id::UUID;"
        },
        {
            "name": "Convert message.id to UUID",
            "sql": "ALTER TABLE message ALTER COLUMN id TYPE UUID USING id::UUID;"
        },
        {
            "name": "Convert message.conversation_id to UUID",
            "sql": "ALTER TABLE message ALTER COLUMN conversation_id TYPE UUID USING conversation_id::UUID;"
        },
        {
            "name": "Recreate message foreign key",
            "sql": "ALTER TABLE message ADD CONSTRAINT message_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES conversation(id);"
        },
    ]

    for step in steps:
        print(f"\n=== {step['name']} ===")
        try:
            with engine.begin() as conn:
                conn.execute(text(step['sql']))
            print(f"✓ {step['name']} - SUCCESS")
        except Exception as e:
            print(f"✗ {step['name']} - FAILED: {e}")

    # Verify the changes
    with engine.connect() as conn:
        print("\n=== AFTER MIGRATION ===")
        result = conn.execute(text("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name IN ('conversation', 'message')
            AND column_name IN ('id', 'user_id', 'conversation_id')
            ORDER BY table_name, ordinal_position;
        """))
        for row in result:
            print(f"{row[0]}.{row[1]}: {row[2]}")

    print("\n✅ Migration complete!")
    print("\nIMPORTANT: Please restart your backend server now:")
    print("  1. Stop the current backend (Ctrl+C)")
    print("  2. Run: cd phase_2_web_App/backend && python app.py")

if __name__ == "__main__":
    run_migration()
