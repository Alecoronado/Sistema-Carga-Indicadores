import sqlite3
import os

# Conectar a la base de datos
db_path = 'indicadores.db'

if not os.path.exists(db_path):
    print(f"❌ Error: No se encontró la base de datos {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("🔄 Iniciando migración de lógica de negocio...\n")
    
    # 1. Agregar fecha_carga a hitos si no existe
    cursor.execute("PRAGMA table_info(hitos)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'fecha_carga' not in columns:
        cursor.execute("ALTER TABLE hitos ADD COLUMN fecha_carga DATE DEFAULT (date('now'))")
        print("✅ Columna 'fecha_carga' agregada a tabla hitos")
    else:
        print("✅ La columna 'fecha_carga' ya existe en hitos")
    
    # 2. Actualizar indicadores existentes sin fecha_carga
    cursor.execute("""
        UPDATE indicadores 
        SET fecha_carga = date('now')
        WHERE fecha_carga IS NULL
    """)
    updated_indicadores = cursor.rowcount
    if updated_indicadores > 0:
        print(f"✅ Actualizada fecha_carga para {updated_indicadores} indicadores")
    else:
        print("✅ Todos los indicadores ya tienen fecha_carga")
    
    # 3. Actualizar hitos existentes con fecha_carga
    cursor.execute("""
        UPDATE hitos 
        SET fecha_carga = date('now')
        WHERE fecha_carga IS NULL
    """)
    updated_hitos = cursor.rowcount
    if updated_hitos > 0:
        print(f"✅ Actualizada fecha_carga para {updated_hitos} hitos")
    else:
        print("✅ Todos los hitos ya tienen fecha_carga")
    
    # 4. Recalcular avance_porcentaje para indicadores cuantitativos (sin hitos)
    # First check if tiene_hitos column exists
    cursor.execute("PRAGMA table_info(indicadores)")
    indicadores_columns = [column[1] for column in cursor.fetchall()]
    
    recalculated = 0  # Initialize here
    
    if 'tiene_hitos' in indicadores_columns:
        cursor.execute("""
            SELECT id, meta, avance, tiene_hitos
            FROM indicadores
            WHERE tiene_hitos = 0 AND meta IS NOT NULL AND avance IS NOT NULL
        """)
        
        indicadores_cuantitativos = cursor.fetchall()
        
        for ind_id, meta, avance, tiene_hitos in indicadores_cuantitativos:
            try:
                meta_num = float(meta)
                if meta_num > 0:
                    avance_porcentaje = int((avance / meta_num) * 100)
                    avance_porcentaje = min(100, max(0, avance_porcentaje))
                    
                    cursor.execute("""
                        UPDATE indicadores
                        SET avance_porcentaje = ?
                        WHERE id = ?
                    """, (avance_porcentaje, ind_id))
                    recalculated += 1
            except ValueError:
                # Meta no es numérica, skip
                pass
        
        if recalculated > 0:
            print(f"✅ Recalculado avance_porcentaje para {recalculated} indicadores cuantitativos")
        else:
            print("✅ No hay indicadores cuantitativos que requieran recálculo")
    else:
        print("⚠️ Columna 'tiene_hitos' no existe aún. Se omite el recálculo de avances.")
    
    conn.commit()
    
    print("\n" + "="*60)
    print("✅ Migración completada exitosamente")
    print("="*60)
    print("\n📋 Resumen:")
    print(f"  - Hitos actualizados: {updated_hitos}")
    print(f"  - Indicadores actualizados: {updated_indicadores}")
    print(f"  - Avances recalculados: {recalculated}")
    print("\n🎯 Ahora puedes reiniciar la aplicación Streamlit")
    
except Exception as e:
    print(f"\n❌ Error durante la migración: {e}")
    conn.rollback()
finally:
    conn.close()
