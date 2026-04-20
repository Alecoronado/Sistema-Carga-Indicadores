"""
Script para verificar el estado de las tablas en PostgreSQL de Railway
"""

import os
import psycopg2

database_url = "postgresql://postgres:kbDblwmlQZflnXYErWrKTKlXJZAQfjBB@hopper.proxy.rlwy.net:18890/railway"

print("=" * 60)
print("VERIFICANDO TABLAS EN POSTGRESQL DE RAILWAY")
print("=" * 60)
print()

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Listar todas las tablas
    print("📋 Listando todas las tablas:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    
    if tables:
        for i, (table,) in enumerate(tables, 1):
            print(f"  {i}. {table}")
    else:
        print("  ⚠️  No se encontraron tablas")
    
    print()
    print("=" * 60)
    
    # Verificar columnas de indicadores
    print("📊 Columnas de la tabla 'indicadores':")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'indicadores'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    if columns:
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
    else:
        print("  ⚠️  Tabla 'indicadores' no encontrada")
    
    print()
    print("=" * 60)
    
    # Verificar columnas de hitos
    print("📊 Columnas de la tabla 'hitos':")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'hitos'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    if columns:
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
    else:
        print("  ⚠️  Tabla 'hitos' no encontrada")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
