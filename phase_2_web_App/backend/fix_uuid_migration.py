"""
Migration script to fix VARCHAR -> UUID conversion for conversation and message tables.

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

    with engine.begin() as conn:
        # Check current state
        print("\n=== BEFORE MIGRATION ===")
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name IN ('conversation', 'message')
            AND column_name IN ('id', 'user_id', 'conversation_id')
            ORDER BY table_name, ordinal_position;
        """))
        for row in result:
            print(f"{row[0]}: {row[1]}")

        # Step 1: Drop foreign key constraint on message.conversation_id
        print("\n=== DROPPING CONSTRAINTS ===")
        try:
            conn.execute(text("ALTER TABLE message DROP CONSTRAINT message_conversation_id_fkey;"))
            print("✓ Dropped message_conversation_id_fkey")
        except Exception as e:
            print(f"  (Constraint may not exist: {e})")

        # Step 2: Drop foreign key constraint on conversation.user_id
        try:
            conn.execute(text("ALTER TABLE conversation DROP CONSTRAINT conversation_user_id_fkey;"))
            print("✓ Dropped conversation_user_id_fkey")
        except Exception as e:
            print(f"  (Constraint may not exist: {e})")

        # Step 3: Convert conversation.id to UUID
        print("\n=== CONVERTING conversation.id ===")
        try:
            conn.execute(text("""
                ALTER TABLE conversation
                ALTER COLUMN id TYPE UUID USING id::UUID;
            """))
            print("✓ Converted conversation.id to UUID")
        except Exception as e:
            print(f"  Error: {e}")

        # Step 4: Convert conversation.user_id to UUID
        print("\n=== CONVERTING conversation.user_id ===")
        try:
            conn.execute(text("""
                ALTER TABLE conversation
                ALTER COLUMN user_id TYPE UUID USING user_id::UUID;
            """))
            print("✓ Converted conversation.user_id to UUID")
        except Exception as e:
            print(f"  Error: {e}")

        # Step 5: Convert message.id to UUID
        print("\n=== CONVERTING message.id ===")
        try:
            conn.execute(text("""
                ALTER TABLE message
                ALTER COLUMN id TYPE UUID USING id::UUID;
            """))
            print("✓ Converted message.id to UUID")
        except Exception as e:
            print(f"  Error: {e}")

        # Step 6: Convert message.conversation_id to UUID
        print("\n=== CONVERTING message.conversation_id ===")
        try:
            conn.execute(text("""
                ALTER TABLE message
                ALTER COLUMN conversation_id TYPE UUID USING conversation_id::UUID;
            """))
            print("✓ Converted message.conversation_id to UUID")
        except Exception as e:
            print(f"  Error: {e}")

        # Step 7: Recreate foreign key constraints
        print("\n=== RECREATING CONSTRAINTS ===")
        try:
            conn.execute(text("""
                ALTER TABLE conversation
                ADD CONSTRAINT conversation_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES "user"(id);
            """))
            print("✓ Recreated conversation_user_id_fkey")
        except Exception as e:
            print(f"  Error: {e}")

        try:
            conn.execute(text("""
                ALTER TABLE message
                ADD CONSTRAINT message_conversation_id_fkey
                FOREIGN KEY (conversation_id) REFERENCES conversation(id);
            """))
            print("✓ Recreated message_conversation_id_fkey")
        except Exception as e:
            print(f"  Error: {e}")

        # Verify the changes
        print("\n=== AFTER MIGRATION ===")
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name IN ('conversation', 'message')
            AND column_name IN ('id', 'user_id', 'conversation_id')
            ORDER BY table_name, ordinal_position;
        """))
        for row in result:
            print(f"{row[0]}: {row[1]}")

    print("\n✅ Migration complete!")
    print("\nNOTE: Please restart your backend server to apply the changes.")

if __name__ == "__main__":
    run_migration()
