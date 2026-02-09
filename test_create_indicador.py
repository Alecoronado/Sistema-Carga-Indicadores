"""
Script de prueba para crear un indicador y ver el error exacto
"""

from database import Database

# Crear instancia de database
db = Database()

print("Intentando crear un indicador de prueba...")
print()

try:
    record_id = db.create_indicador(
        año=2026,
        indicador="Test Indicador",
        tipo_indicador="Estratégico",
        lineamientos_estrategicos="Test",
        responsable="Test User",
        tiene_hitos=True,
        tiene_actividades=False
    )
    print(f"✅ Indicador creado exitosamente con ID: {record_id}")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
