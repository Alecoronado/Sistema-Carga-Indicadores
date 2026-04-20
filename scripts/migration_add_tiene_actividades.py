"""
Migration script to add tiene_actividades column to indicadores table
"""

import os
import sqlite3
import psycopg2
from urllib.parse import urlparse

def migrate_sqlite(db_path='indicadores.db'):
    """Migrate SQLite database"""
    print("🔄 Migrating SQLite database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(indicadores)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tiene_actividades' in columns:
            print("✅ Column 'tiene_actividades' already exists in SQLite")
            conn.close()
            return
        
        # Add tiene_actividades column
        print("➕ Adding 'tiene_actividades' column...")
        cursor.execute("""
            ALTER TABLE indicadores 
            ADD COLUMN tiene_actividades INTEGER DEFAULT 0
        """)
        
        conn.commit()
        print("✅ SQLite migration completed successfully")
        
    except Exception as e:
        print(f"❌ Error during SQLite migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def migrate_postgresql(database_url):
    """Migrate PostgreSQL database"""
    print("🔄 Migrating PostgreSQL database...")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'indicadores' AND column_name = 'tiene_actividades'
        """)
        
        if cursor.fetchone():
            print("✅ Column 'tiene_actividades' already exists in PostgreSQL")
            conn.close()
            return
        
        # Add tiene_actividades column
        print("➕ Adding 'tiene_actividades' column...")
        cursor.execute("""
            ALTER TABLE indicadores 
            ADD COLUMN tiene_actividades BOOLEAN DEFAULT FALSE
        """)
        
        conn.commit()
        print("✅ PostgreSQL migration completed successfully")
        
    except Exception as e:
        print(f"❌ Error during PostgreSQL migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    print("=" * 60)
    print("MIGRATION: Add tiene_actividades to indicadores table")
    print("=" * 60)
    print()
    
    # Check for DATABASE_URL environment variable
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # PostgreSQL migration
        print("📊 Using PostgreSQL from DATABASE_URL")
        migrate_postgresql(database_url)
    else:
        # SQLite migration
        print("📊 Using SQLite (indicadores.db)")
        migrate_sqlite()
    
    print()
    print("=" * 60)
    print("✅ Migration completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
