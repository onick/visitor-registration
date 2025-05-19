#!/usr/bin/env python3
"""
Script para depurar el problema del código de registro
"""
import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8080/api/v1"

def debug_registration_issue():
    print("=== DEPURACIÓN DE CÓDIGO DE REGISTRO ===\n")
    
    # 1. Registrar un visitante
    print("1. Registrando visitante...")
    visitor_data = {
        "name": "Test User " + str(int(time.time())),
        "email": f"test{int(time.time())}@example.com",
        "phone": "809-555-0001",
        "event_id": 1,
        "kiosk_id": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/visitors/register", json=visitor_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            data = response.json()
            code = data.get("registration_code")
            print(f"\nCódigo de registro recibido: {code}")
            
            # 2. Verificar el código inmediatamente
            print("\n2. Verificando código inmediatamente...")
            verify_response = requests.post(f"{BASE_URL}/visitors/verify-code", json={"code": code})
            print(f"Status: {verify_response.status_code}")
            print(f"Response: {json.dumps(verify_response.json(), indent=2)}")
            
            # 3. Verificar con el código en mayúsculas
            print("\n3. Verificando código en mayúsculas...")
            verify_response = requests.post(f"{BASE_URL}/visitors/verify-code", json={"code": code.upper()})
            print(f"Status: {verify_response.status_code}")
            
            # 4. Verificar con el código en minúsculas
            print("\n4. Verificando código en minúsculas...")
            verify_response = requests.post(f"{BASE_URL}/visitors/verify-code", json={"code": code.lower()})
            print(f"Status: {verify_response.status_code}")
            
            # 5. Verificar con el email
            print("\n5. Verificando con email...")
            verify_response = requests.post(f"{BASE_URL}/visitors/verify-code", json={"code": visitor_data["email"]})
            print(f"Status: {verify_response.status_code}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_registration_issue()
