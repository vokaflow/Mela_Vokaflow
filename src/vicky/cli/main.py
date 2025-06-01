"""
CLI principal de Vicky
"""
import click
import logging
import os
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importar comandos
from .commands.voice_commands import voice

@click.group()
def cli():
    """CLI de Vicky - Asistente virtual multimodal"""
    pass

@cli.command()
def version():
    """Muestra la versión de Vicky"""
    click.echo("Vicky v0.1.0")

@cli.command()
@click.argument('message')
def chat(message):
    """Envía un mensaje a Vicky"""
    from ..core.brain import VickyBrain
    
    brain = VickyBrain()
    response = brain.process_message(message)
    click.echo(f"Vicky: {response}")

@cli.command()
@click.argument('text')
@click.option('--source', '-s', help='Idioma de origen (auto-detectado si no se especifica)')
@click.option('--target', '-t', default='es', help='Idioma de destino')
def translate(text, source, target):
    """Traduce un texto usando Vicky"""
    from ..core.brain import VickyBrain
    
    brain = VickyBrain()
    translated = brain.translate(text, source, target)
    click.echo(f"Traducción: {translated}")

# Registrar grupos de comandos
cli.add_command(voice)

if __name__ == '__main__':
    cli()
