#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de Ver Detalles de Evento
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_event_details_view():
    """Probar la navegación a la vista de detalles del evento"""
    # Configurar el navegador
    driver = webdriver.Chrome()  # Asegúrate de tener ChromeDriver instalado
    wait = WebDriverWait(driver, 10)
    
    try:
        # 1. Ir a la página de login
        print("1. Navegando a la página de login...")
        driver.get("http://localhost:8094/login")
        time.sleep(2)
        
        # 2. Hacer login
        print("2. Haciendo login...")
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("Admin123!")
        
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar')]")
        login_button.click()
        
        # Esperar a que cargue el dashboard
        wait.until(EC.url_contains("/admin/dashboard"))
        print("✅ Login exitoso")
        
        # 3. Navegar a la lista de eventos
        print("\n3. Navegando a la lista de eventos...")
        driver.get("http://localhost:8094/admin/events")
        time.sleep(2)
        
        # 4. Encontrar el primer evento y hacer clic en Ver Detalles
        print("\n4. Buscando el botón Ver Detalles...")
        try:
            # Esperar a que carguen los eventos
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "event-card")))
            
            # Encontrar el primer botón Ver Detalles
            ver_detalles_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Ver Detalles')]")
            
            # Obtener el ID del evento del card
            event_card = ver_detalles_btn.find_element(By.XPATH, "./ancestor::div[@class='event-card']")
            
            print("✅ Botón Ver Detalles encontrado")
            
            # 5. Hacer clic en Ver Detalles
            print("\n5. Haciendo clic en Ver Detalles...")
            driver.execute_script("arguments[0].scrollIntoView(true);", ver_detalles_btn)
            time.sleep(1)
            ver_detalles_btn.click()
            
            # 6. Esperar a que cargue la página de detalles
            print("\n6. Esperando página de detalles...")
            time.sleep(3)
            
            # Verificar la URL actual
            current_url = driver.current_url
            print(f"URL actual: {current_url}")
            
            # 7. Verificar que estamos en la página de detalles
            if "/admin/events/" in current_url:
                print("✅ Navegación exitosa a la página de detalles")
                
                # Verificar si hay contenido o error
                try:
                    # Buscar mensaje de error
                    error_msg = driver.find_element(By.XPATH, "//p[contains(text(), 'Evento no encontrado')]")
                    print("❌ ERROR: Se muestra 'Evento no encontrado'")
                    
                    # Verificar la consola del navegador
                    logs = driver.get_log('browser')
                    print("\nLogs de consola:")
                    for log in logs:
                        print(f"  {log['level']}: {log['message']}")
                    
                except:
                    # Si no hay error, buscar el contenido del evento
                    try:
                        event_title = driver.find_element(By.TAG_NAME, "h2")
                        print(f"✅ Evento cargado: {event_title.text}")
                    except:
                        print("❌ No se encontró el título del evento")
                
            else:
                print("❌ No se navegó a la página de detalles")
            
            # 8. Captura de pantalla para debug
            driver.save_screenshot("event_details_test.png")
            print("\n📸 Captura de pantalla guardada como event_details_test.png")
            
        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")
            driver.save_screenshot("error_screenshot.png")
            
    finally:
        print("\nCerrando el navegador...")
        driver.quit()

def test_api_endpoint():
    """Probar directamente el endpoint del API"""
    import requests
    
    print("\n=== Prueba del Endpoint API ===")
    
    # Obtener lista de eventos
    response = requests.get("http://localhost:8080/api/v1/events/")
    if response.status_code == 200:
        events = response.json()
        if events:
            event_id = events[0]['id']
            print(f"Probando con evento ID: {event_id}")
            
            # Probar endpoint de detalles
            detail_response = requests.get(f"http://localhost:8080/api/v1/events/{event_id}")
            print(f"Status: {detail_response.status_code}")
            print(f"Respuesta: {detail_response.json()}")
        else:
            print("No hay eventos disponibles")
    else:
        print(f"Error al obtener eventos: {response.status_code}")

if __name__ == "__main__":
    print("=== Test de Ver Detalles de Evento ===\n")
    
    # Probar la API primero
    test_api_endpoint()
    
    # Luego probar la interfaz
    print("\n=== Test de Interfaz Web ===\n")
    test_event_details_view()
