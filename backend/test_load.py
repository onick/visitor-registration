#!/usr/bin/env python3
"""
Script de prueba de carga para el sistema CCB
Simula múltiples registros concurrentes
"""
import concurrent.futures
import requests
import time
import random
import json
from datetime import datetime

# Configuración
API_URL = "http://localhost:8080/api/v1"
NUM_REQUESTS = 200
MAX_WORKERS = 20

# Nombres y apellidos de ejemplo
NOMBRES = ["Juan", "María", "Pedro", "Ana", "Luis", "Carmen", "José", "Laura", "Miguel", "Sofia"]
APELLIDOS = ["García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores"]

def generate_visitor():
    """Generar datos aleatorios de visitante"""
    nombre = random.choice(NOMBRES)
    apellido = random.choice(APELLIDOS)
    timestamp = int(time.time() * 1000)
    
    return {
        "name": f"{nombre} {apellido}",
        "email": f"{nombre.lower()}.{apellido.lower()}{timestamp % 1000}@example.com",
        "phone": f"809{random.randint(1000000, 9999999)}",
        "event_id": 1
    }

def register_visitor(visitor_data, index):
    """Registrar un visitante y medir tiempo de respuesta"""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/visitors/register",
            json=visitor_data,
            timeout=10
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "index": index,
            "status": response.status_code,
            "duration": duration,
            "success": response.status_code == 201,
            "data": response.json() if response.status_code == 201 else None,
            "error": response.json() if response.status_code != 201 else None
        }
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "index": index,
            "status": 0,
            "duration": duration,
            "success": False,
            "error": str(e)
        }

def run_load_test(num_requests=NUM_REQUESTS, max_workers=MAX_WORKERS):
    """Ejecutar prueba de carga"""
    print(f"=== Prueba de Carga CCB ===")
    print(f"Solicitudes: {num_requests}")
    print(f"Workers concurrentes: {max_workers}")
    print(f"URL: {API_URL}")
    print("\nIniciando prueba...")
    
    # Generar datos de visitantes
    visitors = [generate_visitor() for _ in range(num_requests)]
    
    # Tiempo de inicio
    start_time = time.time()
    results = []
    
    # Ejecutar solicitudes concurrentes
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Crear futures
        futures = [
            executor.submit(register_visitor, visitor, i) 
            for i, visitor in enumerate(visitors)
        ]
        
        # Esperar resultados con barra de progreso
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            results.append(result)
            
            # Mostrar progreso
            progress = (i + 1) / num_requests * 100
            print(f"\rProgreso: {progress:.1f}% ({i + 1}/{num_requests})", end="")
    
    # Tiempo total
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Analizar resultados
    successful = sum(1 for r in results if r["success"])
    failed = num_requests - successful
    avg_duration = sum(r["duration"] for r in results) / num_requests
    max_duration = max(r["duration"] for r in results)
    min_duration = min(r["duration"] for r in results)
    
    # Mostrar resultados
    print("\n\n=== Resultados ===")
    print(f"Tiempo total: {total_duration:.2f} segundos")
    print(f"Solicitudes por segundo: {num_requests / total_duration:.2f}")
    print(f"\nRespuestas:")
    print(f"  Exitosas: {successful} ({successful/num_requests*100:.1f}%)")
    print(f"  Fallidas: {failed} ({failed/num_requests*100:.1f}%)")
    print(f"\nTiempos de respuesta:")
    print(f"  Promedio: {avg_duration:.3f} segundos")
    print(f"  Mínimo: {min_duration:.3f} segundos")
    print(f"  Máximo: {max_duration:.3f} segundos")
    
    # Análisis de errores
    if failed > 0:
        print("\n=== Análisis de Errores ===")
        error_types = {}
        for r in results:
            if not r["success"]:
                error = r.get("error", "Unknown error")
                if isinstance(error, dict):
                    error = error.get("error", str(error))
                error_types[error] = error_types.get(error, 0) + 1
        
        for error, count in error_types.items():
            print(f"  {error}: {count}")
    
    # Guardar resultados detallados
    report_filename = f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump({
            "config": {
                "num_requests": num_requests,
                "max_workers": max_workers,
                "api_url": API_URL
            },
            "summary": {
                "total_duration": total_duration,
                "requests_per_second": num_requests / total_duration,
                "successful": successful,
                "failed": failed,
                "avg_response_time": avg_duration,
                "min_response_time": min_duration,
                "max_response_time": max_duration
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nReporte detallado guardado en: {report_filename}")
    
    return results

def check_database_type():
    """Verificar qué tipo de base de datos está usando el backend"""
    try:
        # Intentar obtener estadísticas
        response = requests.get(f"{API_URL}/visitors/statistics")
        if response.status_code == 200:
            print("✓ Backend está funcionando")
            
            # TODO: Agregar endpoint para verificar tipo de DB
            # Por ahora asumimos que está configurado correctamente
            return True
    except Exception as e:
        print(f"✗ Error conectando al backend: {e}")
        return False

if __name__ == "__main__":
    print("=== Prueba de Carga - Sistema CCB ===\n")
    
    # Verificar backend
    if not check_database_type():
        print("Por favor asegúrate de que el backend esté funcionando")
        exit(1)
    
    # Opciones de prueba
    print("\nOpciones de prueba:")
    print("1. Prueba rápida (50 solicitudes)")
    print("2. Prueba normal (200 solicitudes)")
    print("3. Prueba intensiva (500 solicitudes)")
    print("4. Personalizada")
    
    choice = input("\nSelecciona una opción (1-4): ")
    
    if choice == "1":
        run_load_test(50, 10)
    elif choice == "2":
        run_load_test(200, 20)
    elif choice == "3":
        run_load_test(500, 50)
    elif choice == "4":
        num = int(input("Número de solicitudes: "))
        workers = int(input("Workers concurrentes: "))
        run_load_test(num, workers)
    else:
        print("Opción inválida")
