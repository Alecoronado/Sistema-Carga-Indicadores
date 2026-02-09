"""
Migración para agregar columna tiene_hitos a la tabla indicadores
Esta columna debería existir pero parece que falta en algunas bases de datos
"""

import os
import sqlite3
import psycopg2

def migrate_sqlite(db_path='indicadores.db'):
    """Agregar tiene_hitos a indicadores en SQLite"""
    print("🔄 Verificando SQLite database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(indicadores)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tiene_hitos' not in columns:
            print("➕ Agregando columna 'tiene_hitos' a indicadores...")
            cursor.execute("""
                ALTER TABLE indicadores 
                ADD COLUMN tiene_hitos INTEGER DEFAULT 0
            """)
            conn.commit()
            print("✅ Columna 'tiene_hitos' agregada")
        else:
            print("✅ Columna 'tiene_hitos' ya existe")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def migrate_postgresql(database_url):
    """Agregar tiene_hitos a indicadores en PostgreSQL"""
    print("🔄 Verificando PostgreSQL database...")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'indicadores' AND column_name = 'tiene_hitos'
        """)
        
        if not cursor.fetchone():
            print("➕ Agregando columna 'tiene_hitos' a indicadores...")
            cursor.execute("""
                ALTER TABLE indicadores 
                ADD COLUMN tiene_hitos BOOLEAN DEFAULT FALSE
            """)
            conn.commit()
            print("✅ Columna 'tiene_hitos' agregada")
        else:
            print("✅ Columna 'tiene_hitos' ya existe")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    print("=" * 60)
    print("MIGRACIÓN: Agregar tiene_hitos a indicadores")
    print("=" * 60)
    print()
    
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        migrate_postgresql(database_url)
    else:
        migrate_sqlite()
    
    print()
    print("✅ Migración completada")

if __name__ == "__main__":
    main()
