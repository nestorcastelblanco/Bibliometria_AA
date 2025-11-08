"""
Django management command para ejecutar el scraper de ACM con Playwright
Uso: python manage.py run_scraper --pages 5 --headless
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import subprocess
import sys


class Command(BaseCommand):
    help = 'Ejecuta el scraper de ACM usando Playwright'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=2,
            help='Número de páginas a scrapear (default: 2)'
        )
        parser.add_argument(
            '--no-headless',
            action='store_true',
            help='Ejecutar con interfaz gráfica (solo para desarrollo local)'
        )

    def handle(self, *args, **options):
        max_pages = options['pages']
        headless = not options['no_headless']
        
        self.stdout.write(self.style.SUCCESS(
            f'🚀 Iniciando scraper ACM (páginas={max_pages}, headless={headless})'
        ))
        
        try:
            # Construir ruta al scraper
            scraper_path = settings.BASE_DIR / 'requirement_1' / 'scrapers' / 'acm_scraper_playwright.py'
            
            # Construir comando
            cmd = [sys.executable, str(scraper_path), '--pages', str(max_pages)]
            if not headless:
                cmd.append('--no-headless')
            
            # Ejecutar scraper
            self.stdout.write(f"Ejecutando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=settings.BASE_DIR,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Mostrar output
            if result.stdout:
                self.stdout.write(result.stdout)
            
            self.stdout.write(self.style.SUCCESS(
                f'✅ Scraping completado exitosamente'
            ))
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(
                f'❌ Error en scraping: {e.stderr}'
            ))
            raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'❌ Error: {str(e)}'
            ))
            raise
