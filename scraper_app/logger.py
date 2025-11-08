"""
Sistema de logs para monitorear scrapers y análisis
"""
from django.conf import settings
from pathlib import Path
from datetime import datetime
import json


class ScraperLogger:
    """Logger para scrapers que guarda estado en archivo JSON"""
    
    def __init__(self):
        self.log_dir = settings.BASE_DIR / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / 'scraper_status.json'
    
    def start(self, task_type, params):
        """Registrar inicio de tarea"""
        status = {
            'task_type': task_type,
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'params': params,
            'progress': 0,
            'message': f'{task_type} iniciado'
        }
        self._save_status(status)
        return status
    
    def update(self, progress, message):
        """Actualizar progreso"""
        status = self._load_status()
        status['progress'] = progress
        status['message'] = message
        status['updated_at'] = datetime.now().isoformat()
        self._save_status(status)
    
    def complete(self, message='Completado', results=None):
        """Marcar como completado"""
        status = self._load_status()
        status['status'] = 'completed'
        status['completed_at'] = datetime.now().isoformat()
        status['progress'] = 100
        status['message'] = message
        if results:
            status['results'] = results
        self._save_status(status)
    
    def error(self, error_message):
        """Registrar error"""
        status = self._load_status()
        status['status'] = 'error'
        status['completed_at'] = datetime.now().isoformat()
        status['message'] = error_message
        self._save_status(status)
    
    def get_status(self):
        """Obtener estado actual"""
        return self._load_status()
    
    def _save_status(self, status):
        """Guardar estado en archivo"""
        with open(self.log_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def _load_status(self):
        """Cargar estado desde archivo"""
        if not self.log_file.exists():
            return {
                'status': 'idle',
                'message': 'Sin tareas en ejecución'
            }
        
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except:
            return {
                'status': 'idle',
                'message': 'Sin tareas en ejecución'
            }
