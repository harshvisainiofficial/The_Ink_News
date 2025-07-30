#!/usr/bin/env python3
"""
Database initialization script for The Ink News
Run this script to create all database tables
"""

from main import app, db

def init_database():
    """Initialize the database with all required tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # List all tables created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            raise

if __name__ == '__main__':
    print("🚀 Initializing database for The Ink News...")
    init_database()
    print("✨ Database initialization complete!")