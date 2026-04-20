"""
WORKAROUND: Convertir columnas INTEGER a BOOLEAN en PostgreSQL de Railway
Este script soluciona el problema de tipo de datos hasta que podamos hacer push del código
"""

import psycopg2

database_url = "postgresql://postgres:kbDblwmlQZflnXYErWrKTKlXJZAQfjBB@hopper.proxy.rlwy.net:18890/railway"

print("=" * 60)
print("WORKAROUND: Convertir INTEGER a BOOLEAN en PostgreSQL")
print("=" * 60)
print()

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # 1. Verificar tipo actual de tiene_hitos
    print("1️⃣  Verificando tipo de columna 'tiene_hitos'...")
    cursor.execute("""
        SELECT data_type 
        FROM information_schema.columns 
        WHERE table_name = 'indicadores' AND column_name = 'tiene_hitos'
    """)
    tipo_actual = cursor.fetchone()
    print(f"   Tipo actual: {tipo_actual[0] if tipo_actual else 'NO EXISTE'}")
    
    if tipo_actual and tipo_actual[0] != 'boolean':
        print("   ➕ Convirtiendo a BOOLEAN...")
        
        # Convertir INTEGER a BOOLEAN
        cursor.execute("""
            ALTER TABLE indicadores 
            ALTER COLUMN tiene_hitos TYPE BOOLEAN 
            USING CASE WHEN tiene_hitos = 1 THEN TRUE ELSE FALSE END
        """)
        
        conn.commit()
        print("   ✅ Columna 'tiene_hitos' convertida a BOOLEAN")
    else:
        print("   ✅ Columna ya es BOOLEAN")
    
    print()
    
    # 2. Verificar tipo actual de tiene_actividades
    print("2️⃣  Verificando tipo de columna 'tiene_actividades'...")
    cursor.execute("""
        SELECT data_type 
        FROM information_schema.columns 
        WHERE table_name = 'indicadores' AND column_name = 'tiene_actividades'
    """)
    tipo_actual = cursor.fetchone()
    print(f"   Tipo actual: {tipo_actual[0] if tipo_actual else 'NO EXISTE'}")
    
    if tipo_actual and tipo_actual[0] != 'boolean':
        print("   ➕ Convirtiendo a BOOLEAN...")
        
        # Convertir INTEGER a BOOLEAN
        cursor.execute("""
            ALTER TABLE indicadores 
            ALTER COLUMN tiene_actividades TYPE BOOLEAN 
            USING CASE WHEN tiene_actividades = 1 THEN TRUE ELSE FALSE END
        """)
        
        conn.commit()
        print("   ✅ Columna 'tiene_actividades' convertida a BOOLEAN")
    else:
        print("   ✅ Columna ya es BOOLEAN")
    
    print()
    print("=" * 60)
    print("✅ WORKAROUND COMPLETADO")
    print("=" * 60)
    print()
    print("Ahora puedes crear indicadores en Railway sin errores.")
    print("El código en database.py ya está arreglado localmente.")
    print("Cuando GitHub se recupere, haremos push del código actualizado.")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
