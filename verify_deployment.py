#!/usr/bin/env python3
"""
Script para verificar que la API está lista para deployment en Railway
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NO ENCONTRADO: {filepath}")
        return False

def check_requirements():
    """Check if all required packages are in requirements.txt"""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt no encontrado")
        return False
    
    content = req_file.read_text()
    required_packages = ['fastapi', 'uvicorn', 'pydantic', 'streamlit', 'pandas', 'psycopg2-binary']
    
    missing = []
    for package in required_packages:
        if package not in content.lower():
            missing.append(package)
    
    if missing:
        print(f"❌ Paquetes faltantes en requirements.txt: {', '.join(missing)}")
        return False
    else:
        print("✅ Todos los paquetes requeridos están en requirements.txt")
        return True

def main():
    print("=" * 60)
    print("VERIFICACIÓN DE DEPLOYMENT PARA RAILWAY")
    print("=" * 60)
    print()
    
    checks = []
    
    # Check core files
    print("📁 Verificando archivos principales...")
    checks.append(check_file_exists("app.py", "Aplicación Streamlit"))
    checks.append(check_file_exists("api.py", "API FastAPI"))
    checks.append(check_file_exists("database.py", "Módulo de base de datos"))
    checks.append(check_file_exists("schemas.py", "Schemas Pydantic"))
    checks.append(check_file_exists("styles.py", "Estilos"))
    print()
    
    # Check configuration files
    print("⚙️ Verificando archivos de configuración...")
    checks.append(check_file_exists("requirements.txt", "Requirements"))
    checks.append(check_file_exists("Procfile", "Procfile"))
    checks.append(check_file_exists("railway-api.toml", "Config Railway API"))
    checks.append(check_file_exists("railway-streamlit.toml", "Config Railway Streamlit"))
    print()
    
    # Check migration files
    print("🔄 Verificando archivos de migración...")
    checks.append(check_file_exists("migration_add_responsable_to_hitos.py", "Migración responsable"))
    checks.append(check_file_exists("migration_add_actividades_and_avance_mensual.py", "Migración actividades"))
    print()
    
    # Check requirements content
    print("📦 Verificando dependencias...")
    checks.append(check_requirements())
    print()
    
    # Summary
    print("=" * 60)
    total = len(checks)
    passed = sum(checks)
    
    if passed == total:
        print(f"✅ TODAS LAS VERIFICACIONES PASARON ({passed}/{total})")
        print()
        print("🚀 El proyecto está listo para deployment en Railway!")
        print()
        print("Próximos pasos:")
        print("1. Crear servicio Streamlit en Railway")
        print("2. Crear servicio API en Railway")
        print("3. Configurar DATABASE_URL en ambos servicios")
        print("4. Ejecutar migraciones en producción")
        print()
        print("Ver RAILWAY_DEPLOYMENT.md para instrucciones detalladas")
        return 0
    else:
        print(f"❌ ALGUNAS VERIFICACIONES FALLARON ({passed}/{total})")
        print()
        print("Por favor corrige los errores antes de hacer deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
