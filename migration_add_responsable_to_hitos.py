"""
Migration script to add 'responsable' field to hitos table
This is needed for the Owner monthly reporting workflow
"""

import sqlite3
import os

# Try to import PostgreSQL adapter
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


def run_migration():
    """Run the migration for both SQLite and PostgreSQL"""
    
    print("=" * 60)
    print("MIGRATION: Add responsable field to hitos table")
    print("=" * 60)
    
    # Check for DATABASE_URL (PostgreSQL)
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 is required for PostgreSQL migration")
        migrate_postgresql(database_url)
    else:
        migrate_sqlite()
    
    print("\n✅ Migration completed successfully!")
    print("=" * 60)


def migrate_sqlite(db_path="indicadores.db"):
    """Migrate SQLite database"""
    print(f"\n📦 Migrating SQLite database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(hitos)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'responsable' in columns:
            print("   ℹ️  Column 'responsable' already exists in hitos table")
        else:
            print("\n1️⃣ Adding 'responsable' column to hitos table...")
            cursor.execute("""
                ALTER TABLE hitos ADD COLUMN responsable TEXT
            """)
            print("   ✅ Column 'responsable' added")
        
        conn.commit()
        print("\n✅ SQLite migration completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during migration: {str(e)}")
        raise
    finally:
        conn.close()


def migrate_postgresql(database_url):
    """Migrate PostgreSQL database"""
    print(f"\n🐘 Migrating PostgreSQL database")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'hitos' AND column_name = 'responsable'
        """)
        
        if cursor.fetchone():
            print("   ℹ️  Column 'responsable' already exists in hitos table")
        else:
            print("\n1️⃣ Adding 'responsable' column to hitos table...")
            cursor.execute("""
                ALTER TABLE hitos ADD COLUMN responsable TEXT
            """)
            print("   ✅ Column 'responsable' added")
        
        conn.commit()
        print("\n✅ PostgreSQL migration completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during migration: {str(e)}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
