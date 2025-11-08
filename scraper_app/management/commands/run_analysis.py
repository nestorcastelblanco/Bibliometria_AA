"""
Django management command para ejecutar el pipeline de análisis completo
Uso: python manage.py run_analysis --req2 0 3 7 --req4n 25
"""
from django.core.management.base import BaseCommand
from pathlib import Path
import sys
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parents[4]


class Command(BaseCommand):
    help = 'Ejecuta el pipeline completo de análisis (Req2-5)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bib',
            type=str,
            default='',
            help='Ruta al archivo .bib (si se omite, usa el default)'
        )
        parser.add_argument(
            '--req2',
            type=int,
            nargs='+',
            default=[0, 3, 7],
            help='Índices para Req2 (mín. 2)'
        )
        parser.add_argument(
            '--req4n',
            type=int,
            default=25,
            help='Número de abstracts para Req4'
        )
        parser.add_argument(
            '--wcmax',
            type=int,
            default=150,
            help='Máx. palabras en wordcloud (Req5)'
        )
        parser.add_argument(
            '--topj',
            type=int,
            default=8,
            help='Top N revistas en timeline por journal (Req5)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            '🚀 Iniciando pipeline de análisis completo'
        ))
        
        # Construir comando
        cmd = [sys.executable, str(PROJECT_ROOT / 'run_all.py')]
        
        if options['bib']:
            cmd.extend(['--bib', options['bib']])
        
        cmd.extend(['--req2'] + [str(i) for i in options['req2']])
        cmd.extend(['--req4n', str(options['req4n'])])
        cmd.extend(['--wcmax', str(options['wcmax'])])
        cmd.extend(['--topj', str(options['topj'])])
        
        self.stdout.write(f"Ejecutando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True
            )
            
            self.stdout.write(result.stdout)
            
            self.stdout.write(self.style.SUCCESS(
                '✅ Análisis completado exitosamente'
            ))
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(
                f'❌ Error en análisis: {e.stderr}'
            ))
            raise
