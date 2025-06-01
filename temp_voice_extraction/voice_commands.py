"""
Comandos de CLI para interactuar con el sistema de voz y traducción multimodal
"""
import os
import click
import time
import tempfile
from typing import Optional

from ...core.brain import VickyBrain

@click.group()
def voice():
    """Comandos para trabajar con voz y traducción"""
    pass

@voice.command()
@click.argument('text')
@click.option('--language', '-l', default='es', help='Código de idioma (es, en, fr, etc.)')
@click.option('--gender', '-g', type=click.Choice(['male', 'female']), help='Género de la voz')
@click.option('--emotion', '-e', type=click.Choice(['neutral', 'happy', 'sad', 'angry']), help='Emoción a transmitir')
@click.option('--output', '-o', help='Ruta de salida para el archivo de audio')
def speak(text: str, language: str, gender: Optional[str], emotion: Optional[str], output: Optional[str]):
    """Convierte texto a voz"""
    click.echo(f"Convirtiendo a voz: {text[:50]}...")
    
    brain = VickyBrain()
    
    try:
        audio_path = brain.synthesize_speech(
            text=text,
            language=language,
            gender=gender,
            emotion=emotion,
            output_path=output
        )
        
        click.echo(f"Audio generado: {audio_path}")
        
        # Reproducir audio si es posible
        try:
            import sounddevice as sd
            import soundfile as sf
            
            data, fs = sf.read(audio_path)
            sd.play(data, fs)
            sd.wait()
        except ImportError:
            click.echo("Para reproducir el audio, instala sounddevice y soundfile")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@voice.command()
@click.argument('text')
@click.option('--source', '-s', help='Idioma de origen (auto-detectado si no se especifica)')
@click.option('--target', '-t', default='es', help='Idioma de destino')
@click.option('--gender', '-g', type=click.Choice(['male', 'female']), help='Género de la voz')
@click.option('--emotion', '-e', type=click.Choice(['neutral', 'happy', 'sad', 'angry']), help='Emoción a transmitir')
@click.option('--output', '-o', help='Ruta de salida para el archivo de audio')
def translate_speak(text: str, source: Optional[str], target: str, gender: Optional[str], 
                   emotion: Optional[str], output: Optional[str]):
    """Traduce texto y lo convierte a voz"""
    click.echo(f"Traduciendo y convirtiendo a voz: {text[:50]}...")
    
    brain = VickyBrain()
    
    try:
        result = brain.translate_and_speak(
            text=text,
            source_lang=source,
            target_lang=target,
            gender=gender,
            emotion=emotion,
            output_path=output
        )
        
        if result["success"]:
            click.echo(f"Texto traducido: {result['translated_text']}")
            click.echo(f"Audio generado: {result['audio_path']}")
            
            # Reproducir audio si es posible
            try:
                import sounddevice as sd
                import soundfile as sf
                
                data, fs = sf.read(result['audio_path'])
                sd.play(data, fs)
                sd.wait()
            except ImportError:
                click.echo("Para reproducir el audio, instala sounddevice y soundfile")
        else:
            click.echo(f"Error: {result.get('error', 'Error desconocido')}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@voice.command()
@click.argument('audio_file')
@click.option('--target', '-t', default='es', help='Idioma de destino')
@click.option('--preserve-voice', '-p', is_flag=True, help='Preservar características de la voz original')
@click.option('--output', '-o', help='Ruta de salida para el archivo de audio')
def translate_audio(audio_file: str, target: str, preserve_voice: bool, output: Optional[str]):
    """Traduce un archivo de audio a otro idioma"""
    if not os.path.exists(audio_file):
        click.echo(f"Error: El archivo {audio_file} no existe", err=True)
        return
    
    click.echo(f"Traduciendo audio: {audio_file}")
    
    brain = VickyBrain()
    
    try:
        if preserve_voice:
            click.echo("Usando preservación de voz...")
            result = brain.translate_with_voice_preservation(
                audio_path=audio_file,
                target_lang=target,
                output_path=output
            )
        else:
            result = brain.transcribe_translate_speak(
                audio_path=audio_file,
                target_lang=target,
                output_path=output
            )
        
        if result["success"]:
            click.echo(f"Texto transcrito: {result['transcribed_text']}")
            click.echo(f"Texto traducido: {result['translated_text']}")
            click.echo(f"Audio generado: {result['output_audio']}")
            
            # Reproducir audio si es posible
            try:
                import sounddevice as sd
                import soundfile as sf
                
                data, fs = sf.read(result['output_audio'])
                sd.play(data, fs)
                sd.wait()
            except ImportError:
                click.echo("Para reproducir el audio, instala sounddevice y soundfile")
        else:
            click.echo(f"Error: {result.get('error', 'Error desconocido')}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@voice.command()
@click.option('--language', '-l', help='Filtrar por idioma')
def list_voices(language: Optional[str]):
    """Lista las voces disponibles"""
    brain = VickyBrain()
    
    try:
        # Obtener el modelo TTS
        tts_model = brain.model_manager.get_model("tts")
        
        if not tts_model:
            click.echo("Error: No se pudo cargar el modelo TTS", err=True)
            return
        
        if language:
            voices = tts_model.get_voices_for_language(language)
            click.echo(f"Voces disponibles para {language}:")
            
            for gender, voice_list in voices.items():
                click.echo(f"\n{gender.capitalize()} ({len(voice_list)}):")
                for i, voice in enumerate(voice_list, 1):
                    voice_id = os.path.basename(voice)
                    metadata = tts_model.voice_metadata.get(voice_id, {})
                    quality = metadata.get("quality", "unknown")
                    duration = metadata.get("duration", 0)
                    click.echo(f"  {i}. {voice_id} (Calidad: {quality}, Duración: {duration:.1f}s)")
        else:
            languages = tts_model.get_available_languages()
            click.echo("Idiomas disponibles:")
            
            for lang in languages:
                click.echo(f"  {lang['code']} - {lang['name']} ({lang['voice_count']} voces)")
            
            click.echo("\nUsa 'vicky voice list-voices --language CÓDIGO' para ver las voces de un idioma específico")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@voice.command()
@click.argument('text')
@click.option('--languages', '-l', required=True, help='Códigos de idioma separados por comas (es,en,fr)')
@click.option('--gender', '-g', type=click.Choice(['male', 'female']), help='Género de la voz')
@click.option('--output-dir', '-o', help='Directorio de salida para los archivos de audio')
def multilingual(text: str, languages: str, gender: Optional[str], output_dir: Optional[str]):
    """Genera audio en múltiples idiomas para el mismo texto"""
    language_list = [lang.strip() for lang in languages.split(',')]
    
    if not language_list:
        click.echo("Error: Debes especificar al menos un idioma", err=True)
        return
    
    click.echo(f"Generando audio en {len(language_list)} idiomas: {', '.join(language_list)}")
    
    brain = VickyBrain()
    
    try:
        # Crear directorio de salida si no existe
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = tempfile.gettempdir()
        
        # Obtener el servicio multimodal
        multimodal_service = brain.multimodal_service
        
        result = multimodal_service.create_multilingual_audio(
            text=text,
            languages=language_list,
            gender=gender,
            output_dir=output_dir
        )
        
        if result["success"]:
            click.echo(f"Texto original: {result['original_text']}")
            click.echo(f"Idioma detectado: {result['source_language']}")
            click.echo("\nArchivos de audio generados:")
            
            for lang, audio_path in result["audio_files"].items():
                click.echo(f"  {lang}: {audio_path}")
        else:
            click.echo("Se produjeron errores durante el proceso:")
            for lang, error in result["errors"].items():
                click.echo(f"  {lang}: {error}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
