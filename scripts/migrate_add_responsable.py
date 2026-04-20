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
    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(indicadores)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'responsable' in columns:
        print("✅ La columna 'responsable' ya existe en la tabla indicadores")
    else:
        # Agregar la columna responsable
        cursor.execute("ALTER TABLE indicadores ADD COLUMN responsable TEXT")
        conn.commit()
        print("✅ Columna 'responsable' agregada exitosamente a la tabla indicadores")
    
    # Mostrar estructura actualizada
    cursor.execute("PRAGMA table_info(indicadores)")
    print("\n📋 Estructura actual de la tabla indicadores:")
    for column in cursor.fetchall():
        print(f"  - {column[1]} ({column[2]})")
    
except Exception as e:
    print(f"❌ Error durante la migración: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n✅ Migración completada. Puedes reiniciar la aplicación Streamlit.")
