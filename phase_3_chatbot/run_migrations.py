#!/usr/bin/env python3
"""
Script to run database migrations for the Todo AI Chatbot
"""

import asyncio
import os
from alembic.config import Config
from alembic import command
from database.session import engine
from database.models.base import SQLModel


def run_migrations():
    """Run database migrations using Alembic."""
    # Create alembic config
    alembic_cfg = Config("alembic.ini")

    # Run migrations
    command.upgrade(alembic_cfg, "head")
    print("Database migrations completed successfully!")


def create_tables_directly():
    """Alternative method to create tables directly with SQLModel."""
    from database.models.conversation import Conversation
    from database.models.message import Message
    from database.models.todo import Todo

    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")


if __name__ == "__main__":
    print("Starting database setup...")

    # Try running migrations first
    try:
        run_migrations()
    except Exception as e:
        print(f"Migrations failed: {e}")
        print("Falling back to direct table creation...")
        create_tables_directly()

    print("Database setup completed!")