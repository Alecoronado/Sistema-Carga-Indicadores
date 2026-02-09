"""
Migration script to add 'actividades' and 'avance_mensual' tables
for role-based monthly reporting system

This migration:
1. Creates 'actividades' table (3rd level: Indicador -> Hito -> Actividad)
2. Creates 'avance_mensual' table (monthly historical tracking)
3. Preserves all existing data
"""

import sqlite3
import os
from datetime import datetime

# Try to import PostgreSQL adapter
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


def run_migration():
    """Run the migration for both SQLite and PostgreSQL"""
    
    print("=" * 60)
    print("MIGRATION: Add actividades and avance_mensual tables")
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
        # 1. Create actividades table
        print("\n1️⃣ Creating 'actividades' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hito_id INTEGER NOT NULL,
                descripcion_actividad TEXT NOT NULL,
                fecha_inicio_plan DATE,
                fecha_fin_plan DATE,
                responsable TEXT,
                fecha_real DATE,
                estado_actividad TEXT DEFAULT 'Por comenzar',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hito_id) REFERENCES hitos(id) ON DELETE CASCADE
            )
        """)
        print("   ✅ Table 'actividades' created")
        
        # 2. Create avance_mensual table
        print("\n2️⃣ Creating 'avance_mensual' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avance_mensual (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entidad TEXT NOT NULL CHECK(entidad IN ('hito', 'actividad')),
                id_entidad INTEGER NOT NULL,
                mes TEXT NOT NULL,
                avance_reportado INTEGER NOT NULL CHECK(avance_reportado >= 0 AND avance_reportado <= 100),
                fecha_reporte DATE DEFAULT (date('now')),
                usuario TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(entidad, id_entidad, mes)
            )
        """)
        print("   ✅ Table 'avance_mensual' created")
        
        # 3. Create indexes for performance
        print("\n3️⃣ Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_actividades_hito 
            ON actividades(hito_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_avance_mensual_entidad 
            ON avance_mensual(entidad, id_entidad)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_avance_mensual_mes 
            ON avance_mensual(mes)
        """)
        print("   ✅ Indexes created")
        
        # 4. Migrate existing hito progress to avance_mensual
        print("\n4️⃣ Migrating existing hito progress to avance_mensual...")
        current_month = datetime.now().strftime('%Y-%m')
        
        cursor.execute("""
            SELECT id, avance_porcentaje, updated_at 
            FROM hitos 
            WHERE avance_porcentaje > 0
        """)
        
        hitos_with_progress = cursor.fetchall()
        migrated_count = 0
        
        for hito_id, avance, updated_at in hitos_with_progress:
            # Use the month from updated_at if available, otherwise current month
            try:
                if updated_at:
                    mes = datetime.fromisoformat(updated_at).strftime('%Y-%m')
                else:
                    mes = current_month
            except:
                mes = current_month
            
            cursor.execute("""
                INSERT OR IGNORE INTO avance_mensual 
                (entidad, id_entidad, mes, avance_reportado, fecha_reporte, usuario)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('hito', hito_id, mes, avance, updated_at or datetime.now().date(), 'Sistema (Migración)'))
            
            migrated_count += 1
        
        print(f"   ✅ Migrated {migrated_count} hito progress records")
        
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
        # 1. Create actividades table
        print("\n1️⃣ Creating 'actividades' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actividades (
                id SERIAL PRIMARY KEY,
                hito_id INTEGER NOT NULL,
                descripcion_actividad TEXT NOT NULL,
                fecha_inicio_plan DATE,
                fecha_fin_plan DATE,
                responsable TEXT,
                fecha_real DATE,
                estado_actividad TEXT DEFAULT 'Por comenzar',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hito_id) REFERENCES hitos(id) ON DELETE CASCADE
            )
        """)
        print("   ✅ Table 'actividades' created")
        
        # 2. Create avance_mensual table
        print("\n2️⃣ Creating 'avance_mensual' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avance_mensual (
                id SERIAL PRIMARY KEY,
                entidad TEXT NOT NULL CHECK(entidad IN ('hito', 'actividad')),
                id_entidad INTEGER NOT NULL,
                mes TEXT NOT NULL,
                avance_reportado INTEGER NOT NULL CHECK(avance_reportado >= 0 AND avance_reportado <= 100),
                fecha_reporte DATE DEFAULT CURRENT_DATE,
                usuario TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(entidad, id_entidad, mes)
            )
        """)
        print("   ✅ Table 'avance_mensual' created")
        
        # 3. Create indexes for performance
        print("\n3️⃣ Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_actividades_hito 
            ON actividades(hito_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_avance_mensual_entidad 
            ON avance_mensual(entidad, id_entidad)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_avance_mensual_mes 
            ON avance_mensual(mes)
        """)
        print("   ✅ Indexes created")
        
        # 4. Migrate existing hito progress to avance_mensual
        print("\n4️⃣ Migrating existing hito progress to avance_mensual...")
        current_month = datetime.now().strftime('%Y-%m')
        
        cursor.execute("""
            SELECT id, avance_porcentaje, updated_at 
            FROM hitos 
            WHERE avance_porcentaje > 0
        """)
        
        hitos_with_progress = cursor.fetchall()
        migrated_count = 0
        
        for hito_id, avance, updated_at in hitos_with_progress:
            # Use the month from updated_at if available, otherwise current month
            try:
                if updated_at:
                    mes = updated_at.strftime('%Y-%m')
                else:
                    mes = current_month
            except:
                mes = current_month
            
            cursor.execute("""
                INSERT INTO avance_mensual 
                (entidad, id_entidad, mes, avance_reportado, fecha_reporte, usuario)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (entidad, id_entidad, mes) DO NOTHING
            """, ('hito', hito_id, mes, avance, updated_at or datetime.now().date(), 'Sistema (Migración)'))
            
            migrated_count += 1
        
        print(f"   ✅ Migrated {migrated_count} hito progress records")
        
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
