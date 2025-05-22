"""
Módulo de configuración para la aplicación
"""
from .config import get_config, Config, DevelopmentConfig, TestingConfig, ProductionConfig

__all__ = ['get_config', 'Config', 'DevelopmentConfig', 'TestingConfig', 'ProductionConfig'] 