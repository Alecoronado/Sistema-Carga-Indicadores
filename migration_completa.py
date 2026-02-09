"""
MIGRACIÓN COMPLETA - Sistema de Indicadores
============================================

Esta migración consolida todas las migraciones necesarias en un solo script.
Ejecuta las siguientes operaciones en orden:

1. Agregar columna 'responsable' a tabla 'hitos'
2. Crear tabla 'actividades'
3. Crear tabla 'avance_mensual'
4. Migrar datos existentes de hitos a avance_mensual
5. Agregar columna 'tiene_actividades' a tabla 'indicadores'

Es seguro ejecutar múltiples veces - verifica si cada cambio ya existe antes de aplicarlo.
"""

import os
import sqlite3
import psycopg2
from urllib.parse import urlparse
from datetime import datetime

def migrate_sqlite(db_path='indicadores.db'):
    """Migración completa para SQLite"""
    print("🔄 Migrando SQLite database...")
    print(f"📁 Archivo: {db_path}")
    print()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ===== 1. Agregar 'responsable' a hitos =====
        print("1️⃣  Verificando columna 'responsable' en tabla 'hitos'...")
        cursor.execute("PRAGMA table_info(hitos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'responsable' not in columns:
            print("   ➕ Agregando columna 'responsable'...")
            cursor.execute("ALTER TABLE hitos ADD COLUMN responsable TEXT")
            conn.commit()
            print("   ✅ Columna 'responsable' agregada")
        else:
            print("   ✅ Columna 'responsable' ya existe")
        print()
        
        # ===== 2. Crear tabla 'actividades' =====
        print("2️⃣  Verificando tabla 'actividades'...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='actividades'
        """)
        
        if not cursor.fetchone():
            print("   ➕ Creando tabla 'actividades'...")
            cursor.execute("""
                CREATE TABLE actividades (
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
            conn.commit()
            print("   ✅ Tabla 'actividades' creada")
        else:
            print("   ✅ Tabla 'actividades' ya existe")
        print()
        
        # ===== 3. Crear tabla 'avance_mensual' =====
        print("3️⃣  Verificando tabla 'avance_mensual'...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='avance_mensual'
        """)
        
        if not cursor.fetchone():
            print("   ➕ Creando tabla 'avance_mensual'...")
            cursor.execute("""
                CREATE TABLE avance_mensual (
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
            
            cursor.execute("""
                CREATE INDEX idx_avance_mensual_entidad 
                ON avance_mensual(entidad, id_entidad)
            """)
            
            cursor.execute("""
                CREATE INDEX idx_avance_mensual_mes 
                ON avance_mensual(mes)
            """)
            
            conn.commit()
            print("   ✅ Tabla 'avance_mensual' creada con índices")
            
            # Migrar datos existentes
            print("   📊 Migrando datos existentes de hitos...")
            cursor.execute("""
                SELECT id, avance_porcentaje 
                FROM hitos 
                WHERE avance_porcentaje > 0
            """)
            hitos_con_avance = cursor.fetchall()
            
            if hitos_con_avance:
                mes_actual = datetime.now().strftime('%Y-%m')
                for hito_id, avance in hitos_con_avance:
                    cursor.execute("""
                        INSERT OR IGNORE INTO avance_mensual 
                        (entidad, id_entidad, mes, avance_reportado, usuario)
                        VALUES ('hito', ?, ?, ?, 'Sistema - Migración')
                    """, (hito_id, mes_actual, avance))
                conn.commit()
                print(f"   ✅ Migrados {len(hitos_con_avance)} registros de avance")
            else:
                print("   ℹ️  No hay datos de avance para migrar")
        else:
            print("   ✅ Tabla 'avance_mensual' ya existe")
        print()
        
        # ===== 4. Agregar 'tiene_actividades' a indicadores =====
        print("4️⃣  Verificando columna 'tiene_actividades' en tabla 'indicadores'...")
        cursor.execute("PRAGMA table_info(indicadores)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tiene_actividades' not in columns:
            print("   ➕ Agregando columna 'tiene_actividades'...")
            cursor.execute("""
                ALTER TABLE indicadores 
                ADD COLUMN tiene_actividades INTEGER DEFAULT 0
            """)
            conn.commit()
            print("   ✅ Columna 'tiene_actividades' agregada")
        else:
            print("   ✅ Columna 'tiene_actividades' ya existe")
        print()
        
        print("=" * 60)
        print("✅ MIGRACIÓN SQLITE COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error durante la migración SQLite: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate_postgresql(database_url):
    """Migración completa para PostgreSQL"""
    print("🔄 Migrando PostgreSQL database...")
    print(f"🔗 Conectando a: {database_url.split('@')[1] if '@' in database_url else 'Railway'}")
    print()
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # ===== 1. Agregar 'responsable' a hitos =====
        print("1️⃣  Verificando columna 'responsable' en tabla 'hitos'...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'hitos' AND column_name = 'responsable'
        """)
        
        if not cursor.fetchone():
            print("   ➕ Agregando columna 'responsable'...")
            cursor.execute("ALTER TABLE hitos ADD COLUMN responsable TEXT")
            conn.commit()
            print("   ✅ Columna 'responsable' agregada")
        else:
            print("   ✅ Columna 'responsable' ya existe")
        print()
        
        # ===== 2. Crear tabla 'actividades' =====
        print("2️⃣  Verificando tabla 'actividades'...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'actividades'
            )
        """)
        
        if not cursor.fetchone()[0]:
            print("   ➕ Creando tabla 'actividades'...")
            cursor.execute("""
                CREATE TABLE actividades (
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
            conn.commit()
            print("   ✅ Tabla 'actividades' creada")
        else:
            print("   ✅ Tabla 'actividades' ya existe")
        print()
        
        # ===== 3. Crear tabla 'avance_mensual' =====
        print("3️⃣  Verificando tabla 'avance_mensual'...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'avance_mensual'
            )
        """)
        
        if not cursor.fetchone()[0]:
            print("   ➕ Creando tabla 'avance_mensual'...")
            cursor.execute("""
                CREATE TABLE avance_mensual (
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
            
            cursor.execute("""
                CREATE INDEX idx_avance_mensual_entidad 
                ON avance_mensual(entidad, id_entidad)
            """)
            
            cursor.execute("""
                CREATE INDEX idx_avance_mensual_mes 
                ON avance_mensual(mes)
            """)
            
            conn.commit()
            print("   ✅ Tabla 'avance_mensual' creada con índices")
            
            # Migrar datos existentes
            print("   📊 Migrando datos existentes de hitos...")
            cursor.execute("""
                SELECT id, avance_porcentaje 
                FROM hitos 
                WHERE avance_porcentaje > 0
            """)
            hitos_con_avance = cursor.fetchall()
            
            if hitos_con_avance:
                mes_actual = datetime.now().strftime('%Y-%m')
                for hito_id, avance in hitos_con_avance:
                    cursor.execute("""
                        INSERT INTO avance_mensual 
                        (entidad, id_entidad, mes, avance_reportado, usuario)
                        VALUES ('hito', %s, %s, %s, 'Sistema - Migración')
                        ON CONFLICT (entidad, id_entidad, mes) DO NOTHING
                    """, (hito_id, mes_actual, avance))
                conn.commit()
                print(f"   ✅ Migrados {len(hitos_con_avance)} registros de avance")
            else:
                print("   ℹ️  No hay datos de avance para migrar")
        else:
            print("   ✅ Tabla 'avance_mensual' ya existe")
        print()
        
        # ===== 4. Agregar 'tiene_actividades' a indicadores =====
        print("4️⃣  Verificando columna 'tiene_actividades' en tabla 'indicadores'...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'indicadores' AND column_name = 'tiene_actividades'
        """)
        
        if not cursor.fetchone():
            print("   ➕ Agregando columna 'tiene_actividades'...")
            cursor.execute("""
                ALTER TABLE indicadores 
                ADD COLUMN tiene_actividades BOOLEAN DEFAULT FALSE
            """)
            conn.commit()
            print("   ✅ Columna 'tiene_actividades' agregada")
        else:
            print("   ✅ Columna 'tiene_actividades' ya existe")
        print()
        
        print("=" * 60)
        print("✅ MIGRACIÓN POSTGRESQL COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error durante la migración PostgreSQL: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    print()
    print("=" * 60)
    print("  MIGRACIÓN COMPLETA - SISTEMA DE INDICADORES")
    print("=" * 60)
    print()
    print("Esta migración incluye:")
    print("  1. Columna 'responsable' en hitos")
    print("  2. Tabla 'actividades'")
    print("  3. Tabla 'avance_mensual'")
    print("  4. Migración de datos existentes")
    print("  5. Columna 'tiene_actividades' en indicadores")
    print()
    print("=" * 60)
    print()
    
    # Check for DATABASE_URL environment variable
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # PostgreSQL migration
        print("📊 Usando PostgreSQL (DATABASE_URL detectada)")
        print()
        migrate_postgresql(database_url)
    else:
        # SQLite migration
        print("📊 Usando SQLite local (indicadores.db)")
        print()
        migrate_sqlite()
    
    print()
    print("=" * 60)
    print("🎉 ¡TODAS LAS MIGRACIONES COMPLETADAS!")
    print("=" * 60)
    print()
    print("Tablas creadas/actualizadas:")
    print("  ✅ indicadores (con tiene_actividades)")
    print("  ✅ hitos (con responsable)")
    print("  ✅ actividades")
    print("  ✅ avance_mensual")
    print()

if __name__ == "__main__":
    main()
