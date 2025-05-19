#!/usr/bin/env python3
"""
Script simple para probar el registro y check-in
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8080/api/v1"

def test_simple():
    print("=== TEST SIMPLE DE REGISTRO Y CHECK-IN ===\n")
    
    # 1. Registrar un visitante
    print("1. Registrando visitante...")
    visitor_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "809-555-0001",
        "event_id": 1,
        "kiosk_id": 1
    }
    
    response = requests.post(f"{BASE_URL}/visitors/register", json=visitor_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        data = response.json()
        code = data.get("registration_code")
        print(f"Código de registro: {code}")
        
        # 2. Verificar el código
        print("\n2. Verificando código...")
        verify_response = requests.post(f"{BASE_URL}/visitors/verify-code", json={"code": code})
        print(f"Status: {verify_response.status_code}")
        print(f"Response: {verify_response.text}")

if __name__ == "__main__":
    test_simple()
