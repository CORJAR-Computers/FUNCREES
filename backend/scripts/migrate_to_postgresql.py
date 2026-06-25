"""
============================================
 MIGRACIÓN: SQLite → PostgreSQL (Neon)
============================================

Este script te guía en la migración de datos desde SQLite local
hacia PostgreSQL en Neon (serverless).

REQUISITOS:
  1. Tener una cuenta en Neon (https://neon.tech)
  2. Crear un proyecto y obtener la DATABASE_URL
  3. pip install psycopg2-binary

PASOS:
  1. Ejecuta: python manage.py dumpdata --natural-foreign --natural-primary > data_dump.json
  2. Cambia DATABASE_URL en .env a la de Neon
  3. Ejecuta: python manage.py migrate
  4. Ejecuta: python manage.py loaddata data_dump.json
  5. Verifica: python manage.py createsuperuser (si no existe)
"""

import subprocess
import sys
import os

STEPS = [
    {
        "name": "1. Exportar datos desde SQLite",
        "cmd": "python manage.py dumpdata --natural-foreign --natural-primary --exclude=contenttypes --exclude=auth.permission > data_dump.json",
        "check": "data_dump.json"
    },
    {
        "name": "2. Configurar .env para PostgreSQL",
        "msg": "Edita backend/.env y cambia DATABASE_URL a tu URL de Neon:\n  DATABASE_URL=postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/funcrees_db?sslmode=require"
    },
    {
        "name": "3. Ejecutar migraciones en PostgreSQL",
        "cmd": "python manage.py migrate"
    },
    {
        "name": "4. Cargar datos en PostgreSQL",
        "cmd": "python manage.py loaddata data_dump.json"
    },
    {
        "name": "5. Verificar datos cargados",
        "cmd": "python manage.py shell -c \"from beneficiaries.models import Beneficiary; print(f'Beneficiarios: {Beneficiary.objects.count()}')\""
    },
]


def run():
    print("=" * 60)
    print("  🚀 MIGRACIÓN: SQLite → PostgreSQL (Neon)")
    print("=" * 60)

    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        print("❌ ERROR: Debes ejecutar este script desde backend/")
        print("   cd backend")
        print(f"   python {os.path.basename(__file__)}")
        sys.exit(1)

    for step in STEPS:
        print(f"\n{'─' * 60}")
        print(f"  {step['name']}")
        print(f"{'─' * 60}")

        if 'cmd' in step and 'msg' in step:
            print(f"\n  Comando: {step['cmd']}\n")
            print(f"  ⚠️  {step['msg']}")
            input("\n  Presiona Enter cuando hayas completado este paso...")
        elif 'cmd' in step:
            print(f"\n  Ejecutando: {step['cmd']}\n")
            result = subprocess.run(step['cmd'], shell=True, capture_output=False)
            if result.returncode != 0:
                print(f"\n  ⚠️  El comando terminó con código {result.returncode}")
                print("  Puedes continuar o revisar el error.")
        elif 'msg' in step:
            print(f"\n  {step['msg']}")
            if step.get('check'):
                check_path = step['check']
                if os.path.exists(check_path):
                    print(f"\n  ✅ {check_path} creado exitosamente")
            input("\n  Presiona Enter cuando hayas completado este paso...")

    print(f"\n{'=' * 60}")
    print("  ✅ MIGRACIÓN COMPLETADA")
    print("  Recuerda: ")
    print("  - Verificar que todas las tablas tengan datos")
    print("  - Crear un superusuario: python manage.py createsuperuser")
    print("  - Eliminar data_dump.json por seguridad")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    run()
