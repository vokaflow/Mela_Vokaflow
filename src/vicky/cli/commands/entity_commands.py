"""
Comandos CLI para el Sistema de Extracción de Entidades
-------------------------------------------------------

Este módulo implementa comandos para la interfaz de línea de comandos
que permiten interactuar con el sistema de extracción de entidades,
probar la extracción, gestionar reglas y realizar análisis de textos.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import click
import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict
import pprint
import time
from tabulate import tabulate

# Añadir directorio raíz al path si es necesario
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.vicky.core.entity_extractor import EntityExtractor, ExtractionRule
from src.vicky.core.entity_types import Entity, EntityGroup, EntityCategory, EntitySubType, ENTITY_RELATIONS


@click.group(name="entity")
def entity_commands():
    """Comandos para el sistema de extracción de entidades."""
    pass


@entity_commands.command("extract")
@click.argument("text", required=True)
@click.option("--output", "-o", type=click.Path(), help="Guardar resultados en archivo JSON")
@click.option("--verbose", "-v", is_flag=True, help="Mostrar información detallada")
@click.option("--format", "-f", type=click.Choice(["table", "json", "pretty"]), default="table", help="Formato de salida")
def extract_entities(text: str, output: Optional[str], verbose: bool, format: str):
    """
    Extraer entidades de un texto.
    
    TEXT: Texto a analizar (usar comillas para textos con espacios)
    """
    try:
        # Inicializar extractor
        extractor = EntityExtractor()
        
        # Medir tiempo
        start_time = time.time()
        
        # Extraer entidades
        entities = extractor.extract_entities(text)
        
        # Calcular tiempo
        processing_time = time.time() - start_time
        
        # Mostrar resultados según formato
        if format == "table":
            # Crear tabla
            headers = ["ID", "Nombre", "Categoría", "Subtipo", "Confianza", "Posición"]
            rows = []
            
            for entity in entities:
                rows.append([
                    entity.id[:8] + "...",  # ID abreviado
                    entity.name[:30] + "..." if len(entity.name) > 30 else entity.name,
                    entity.category.name,
                    entity.subtype.name if entity.subtype else "N/A",
                    f"{entity.confidence:.2f}",
                    f"{entity.start_pos}-{entity.end_pos}" if entity.start_pos >= 0 else "N/A"
                ])
            
            click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
            click.echo(f"\nSe encontraron {len(entities)} entidades en {processing_time:.3f} segundos.")
            
            # Mostrar estadísticas por categoría
            if verbose:
                categories = {}
                for entity in entities:
                    cat = entity.category.name
                    categories[cat] = categories.get(cat, 0) + 1
                
                click.echo("\nDistribución por categoría:")
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    click.echo(f"  - {cat}: {count}")
        
        elif format == "json":
            # Convertir a JSON
            result = {
                "text": text,
                "entities": [entity.to_dict() for entity in entities],
                "processing_time": processing_time,
                "count": len(entities)
            }
            
            # Mostrar JSON
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif format == "pretty":
            # Mostrar detalle de cada entidad
            click.echo(f"Texto analizado: {text}")
            click.echo(f"\nSe encontraron {len(entities)} entidades en {processing_time:.3f} segundos:\n")
            
            for i, entity in enumerate(entities):
                click.echo(f"Entidad {i+1}:")
                click.echo(f"  ID: {entity.id}")
                click.echo(f"  Nombre: {entity.name}")
                click.echo(f"  Categoría: {entity.category.name}")
                click.echo(f"  Subtipo: {entity.subtype.name if entity.subtype else 'N/A'}")
                click.echo(f"  Valor: {entity.value}")
                click.echo(f"  Posición: {entity.start_pos}-{entity.end_pos}" if entity.start_pos >= 0 else "  Posición: N/A")
                click.echo(f"  Confianza: {entity.confidence:.2f}")
                click.echo(f"  Fuente: {entity.source}")
                
                if entity.attributes and verbose:
                    click.echo("  Atributos:")
                    for key, value in entity.attributes.items():
                        click.echo(f"    - {key}: {value}")
                
                if entity.relations and verbose:
                    click.echo("  Relaciones:")
                    for rel_id, rel_type in entity.relations:
                        target = next((e for e in entities if e.id == rel_id), None)
                        target_name = target.name if target else f"<Entidad {rel_id[:8]}...>"
                        click.echo(f"    - {rel_type} → {target_name}")
                
                click.echo("")
        
        # Guardar en archivo si se especificó
        if output:
            result = {
                "text": text,
                "entities": [entity.to_dict() for entity in entities],
                "processing_time": processing_time,
                "count": len(entities)
            }
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            click.echo(f"Resultados guardados en {output}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@entity_commands.command("list-rules")
@click.option("--enabled-only", "-e", is_flag=True, help="Mostrar solo reglas habilitadas")
@click.option("--category", "-c", help="Filtrar por categoría")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table", help="Formato de salida")
def list_rules(enabled_only: bool, category: Optional[str], format: str):
    """Listar reglas de extracción disponibles."""
    try:
        # Inicializar extractor
        extractor = EntityExtractor()
        
        # Obtener reglas
        rules = extractor.get_rules()
        
        # Filtrar si es necesario
        if enabled_only:
            rules = {k: v for k, v in rules.items() if v.enabled}
        
        if category:
            # Intentar convertir a enum
            try:
                cat_enum = EntityCategory[category.upper()]
                rules = {k: v for k, v in rules.items() if v.category == cat_enum}
            except KeyError:
                click.echo(f"Error: Categoría '{category}' no válida.", err=True)
                click.echo(f"Categorías disponibles: {', '.join([c.name for c in EntityCategory])}")
                sys.exit(1)
        
        # Mostrar resultados según formato
        if format == "table":
            headers = ["ID", "Nombre", "Categoría", "Subtipo", "Confianza", "Prioridad", "Habilitada"]
            rows = []
            
            for rule_id, rule in sorted(rules.items(), key=lambda x: x[1].priority, reverse=True):
                rows.append([
                    rule_id,
                    rule.name,
                    rule.category.name,
                    rule.subtype.name if rule.subtype else "N/A",
                    f"{rule.confidence:.2f}",
                    rule.priority,
                    "✓" if rule.enabled else "✗"
                ])
            
            click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
            click.echo(f"\nTotal: {len(rules)} reglas")
            
        elif format == "json":
            # Convertir a JSON
            result = {
                rule_id: {
                    "name": rule.name,
                    "pattern": rule.pattern,
                    "category": rule.category.name,
                    "subtype": rule.subtype.name if rule.subtype else None,
                    "confidence": rule.confidence,
                    "priority": rule.priority,
                    "enabled": rule.enabled
                } for rule_id, rule in rules.items()
            }
            
            # Mostrar JSON
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@entity_commands.command("test-file")
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Guardar resultados en archivo JSON")
@click.option("--format", "-f", type=click.Choice(["summary", "detailed", "json"]), default="summary", help="Formato de salida")
def test_file(file: str, output: Optional[str], format: str):
    """
    Extraer entidades de un archivo de texto.
    
    FILE: Ruta al archivo de texto
    """
    try:
        # Leer archivo
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Inicializar extractor
        extractor = EntityExtractor()
        
        # Medir tiempo
        start_time = time.time()
        
        # Extraer entidades
        entities = extractor.extract_entities(text)
        
        # Calcular tiempo
        processing_time = time.time() - start_time
        
        # Preparar resultados
        result = {
            "filename": file,
            "text_length": len(text),
            "entities_count": len(entities),
            "processing_time": processing_time,
            "entities": [entity.to_dict() for entity in entities]
        }
        
        # Mostrar resultados según formato
        if format == "summary":
            click.echo(f"Archivo: {file}")
            click.echo(f"Longitud del texto: {len(text)} caracteres")
            click.echo(f"Entidades encontradas: {len(entities)}")
            click.echo(f"Tiempo de procesamiento: {processing_time:.3f} segundos")
            
            # Mostrar distribución por categoría
            categories = {}
            for entity in entities:
                cat = entity.category.name
                categories[cat] = categories.get(cat, 0) + 1
            
            click.echo("\nDistribución por categoría:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(entities)) * 100 if entities else 0
                click.echo(f"  - {cat}: {count} ({percentage:.1f}%)")
        
        elif format == "detailed":
            click.echo(f"Archivo: {file}")
            click.echo(f"Longitud del texto: {len(text)} caracteres")
            click.echo(f"Entidades encontradas: {len(entities)}")
            click.echo(f"Tiempo de procesamiento: {processing_time:.3f} segundos")
            
            # Mostrar entidades por categoría
            categories = {}
            for entity in entities:
                cat = entity.category.name
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(entity)
            
            for cat, cat_entities in sorted(categories.items()):
                click.echo(f"\n=== {cat} ({len(cat_entities)}) ===")
                for entity in cat_entities[:10]:  # Limitar a 10 por categoría
                    subtype = entity.subtype.name if entity.subtype else "N/A"
                    click.echo(f"  - {entity.name} ({subtype}, conf: {entity.confidence:.2f})")
                
                if len(cat_entities) > 10:
                    click.echo(f"  ... y {len(cat_entities) - 10} más")
        
        elif format == "json":
            # Mostrar JSON
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Guardar en archivo si se especificó
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            click.echo(f"Resultados guardados en {output}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@entity_commands.command("benchmark")
@click.option("--tests", "-t", type=int, default=10, help="Número de textos a generar")
@click.option("--output", "-o", type=click.Path(), help="Directorio para guardar resultados")
@click.option("--verbose", "-v", is_flag=True, help="Mostrar información detallada")
def run_benchmark(tests: int, output: Optional[str], verbose: bool):
    """Ejecutar benchmark del extractor de entidades."""
    try:
        # Importar módulo de benchmark
        from src.vicky.core.entity_extractor import EntityExtractor
        import random
        import string
        import matplotlib.pyplot as plt
        import numpy as np
        
        click.echo(f"Ejecutando benchmark con {tests} textos...")
        
        # Inicializar extractor
        extractor = EntityExtractor()
        
        # Generar textos de prueba
        test_data = []
        
        # Plantillas básicas para generar texto
        templates = [
            "El usuario {nombre} trabaja en {empresa} como {rol}.",
            "El proyecto utiliza {tecnologia} con {framework} para el backend.",
            "La reunión está programada para el {fecha} a las {hora}.",
            "El costo del proyecto es de {cantidad}€ para un total de {duracion} semanas.",
            "Para más información, visita {url} o contacta con {email}.",
            "La función {funcion} procesa datos y genera un resultado {tipo}."
        ]
        
        nombres = ["Juan Pérez", "María García", "Carlos Rodríguez", "Ana Martínez"]
        empresas = ["Google", "Microsoft", "Amazon", "Meta", "IBM"]
        roles = ["desarrollador", "gerente", "analista", "diseñador"]
        tecnologias = ["Python", "JavaScript", "Java", "C++", "Go"]
        frameworks = ["Django", "React", "Spring", "Angular", "Express"]
        fechas = ["15/01/2023", "28/02/2023", "10/03/2023", "22/04/2023"]
        horas = ["09:00", "10:30", "12:15", "14:45", "16:30"]
        cantidades = ["1.500", "2.999,99", "10.000", "5.250,50", "999"]
        duraciones = ["2", "4", "6", "8", "12"]
        urls = ["https://example.com", "https://github.com/proyecto", "https://dev.to/articulo"]
        emails = ["contacto@empresa.com", "info@proyecto.org", "soporte@app.io"]
        funciones = ["calculate_total()", "process_data(input)", "validate_user(id, token)"]
        tipos = ["numérico", "textual", "binario", "estructurado"]
        
        for i in range(tests):
            # Seleccionar plantillas aleatorias para este texto
            selected_templates = random.sample(templates, min(random.randint(2, 4), len(templates)))
            
            # Rellenar plantillas
            sentences = []
            for template in selected_templates:
                filled = template.format(
                    nombre=random.choice(nombres),
                    empresa=random.choice(empresas),
                    rol=random.choice(roles),
                    tecnologia=random.choice(tecnologias),
                    framework=random.choice(frameworks),
                    fecha=random.choice(fechas),
                    hora=random.choice(horas),
                    cantidad=random.choice(cantidades),
                    duracion=random.choice(duraciones),
                    url=random.choice(urls),
                    email=random.choice(emails),
                    funcion=random.choice(funciones),
                    tipo=random.choice(tipos)
                )
                sentences.append(filled)
            
            # Crear texto combinando oraciones
            text = " ".join(sentences)
            test_data.append({"text": text, "length": len(text)})
        
        # Ejecutar benchmark
        results = []
        for i, item in enumerate(test_data):
            text = item["text"]
            
            if verbose:
                click.echo(f"\nProcesando texto {i+1}/{len(test_data)} ({item['length']} caracteres)")
                click.echo(f"Texto: {text}")
            
            # Medir tiempo
            start_time = time.time()
            entities = extractor.extract_entities(text)
            processing_time = time.time() - start_time
            
            # Guardar resultados
            result = {
                "text_length": item["length"],
                "entities_count": len(entities),
                "processing_time": processing_time,
                "categories": {}
            }
            
            # Contar entidades por categoría
            for entity in entities:
                cat = entity.category.name
                result["categories"][cat] = result["categories"].get(cat, 0) + 1
            
            results.append(result)
            
            if verbose:
                click.echo(f"Entidades
