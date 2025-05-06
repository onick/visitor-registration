"""
Configuración de Gunicorn para desarrollo
"""
import multiprocessing

# Configuración del servidor
bind = "0.0.0.0:8080"
workers = 2  # Para desarrollo 2 es suficiente

# Configuración de recarga automática para desarrollo
reload = True
reload_engine = "auto"

# Configuración de logs
loglevel = "info"
accesslog = "-"  # Enviar a stdout
errorlog = "-"   # Enviar a stderr

# Configuración de tiempos de espera
timeout = 120     # 2 minutos
graceful_timeout = 10

# Configuración de trabajadores
worker_class = "sync"
threads = 2
