#!/usr/bin/env python3
"""
🔍 VokaFlow Router Identifier - Identificación completa de todos los routers
Análisis sistemático de todos los routers disponibles en VokaFlow Backend
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any
import json

def analyze_router_file(router_path: str) -> Dict[str, Any]:
    """Analizar un archivo de router y extraer información"""
    try:
        with open(router_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Información básica
        info = {
            "file_path": router_path,
            "file_size": os.path.getsize(router_path),
            "lines_count": len(content.split('\n')),
            "has_router": "router = APIRouter" in content or "router=" in content,
            "endpoints": [],
            "imports": [],
            "description": "",
            "tags": [],
            "prefix": "",
            "status": "unknown"
        }
        
        # Extraer descripción del docstring
        lines = content.split('\n')
        in_docstring = False
        docstring_lines = []
        
        for line in lines:
            if '"""' in line and not in_docstring:
                in_docstring = True
                docstring_lines.append(line.replace('"""', '').strip())
            elif '"""' in line and in_docstring:
                in_docstring = False
                break
            elif in_docstring:
                docstring_lines.append(line.strip())
        
        if docstring_lines:
            info["description"] = ' '.join(docstring_lines).strip()
        
        # Buscar endpoints (decoradores @router)
        endpoint_patterns = ["@router.get", "@router.post", "@router.put", "@router.delete", "@router.patch"]
        current_endpoint = None
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Buscar decoradores de endpoint
            for pattern in endpoint_patterns:
                if stripped_line.startswith(pattern):
                    method = pattern.replace("@router.", "").upper()
                    # Extraer la ruta
                    if '("' in stripped_line:
                        path = stripped_line.split('("')[1].split('"')[0]
                    elif "('" in stripped_line:
                        path = stripped_line.split("('")[1].split("'")[0]
                    else:
                        path = "unknown"
                    
                    current_endpoint = {
                        "method": method,
                        "path": path,
                        "line": i + 1,
                        "function": "",
                        "description": ""
                    }
                    break
            
            # Buscar función del endpoint
            if current_endpoint and stripped_line.startswith("async def ") or stripped_line.startswith("def "):
                func_name = stripped_line.split("def ")[1].split("(")[0]
                current_endpoint["function"] = func_name
                info["endpoints"].append(current_endpoint)
                current_endpoint = None
        
        # Buscar imports importantes
        for line in lines:
            if line.strip().startswith("from ") or line.strip().startswith("import "):
                info["imports"].append(line.strip())
        
        # Buscar tags y prefix
        if "tags=[" in content:
            try:
                tags_start = content.find("tags=[")
                tags_end = content.find("]", tags_start)
                tags_text = content[tags_start:tags_end+1]
                info["tags"] = eval(tags_text.replace("tags=", ""))
            except:
                pass
        
        if 'prefix="' in content:
            try:
                prefix_start = content.find('prefix="') + 8
                prefix_end = content.find('"', prefix_start)
                info["prefix"] = content[prefix_start:prefix_end]
            except:
                pass
        
        # Determinar estado
        if info["has_router"] and info["endpoints"]:
            info["status"] = "active"
        elif info["has_router"]:
            info["status"] = "configured"
        else:
            info["status"] = "inactive"
            
        return info
        
    except Exception as e:
        return {
            "file_path": router_path,
            "error": str(e),
            "status": "error"
        }

def get_router_imports_from_main() -> List[str]:
    """Extraer las importaciones de routers desde main.py"""
    try:
        with open("src/main.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            if "from src.backend.routers." in line and "import router as" in line:
                router_name = line.split("from src.backend.routers.")[1].split(" import")[0]
                alias = line.split("as ")[1].strip()
                imports.append({
                    "module": router_name,
                    "alias": alias,
                    "line": line.strip()
                })
        
        return imports
    except Exception as e:
        print(f"Error reading main.py: {e}")
        return []

def get_router_registrations_from_main() -> List[str]:
    """Extraer los registros de routers desde main.py"""
    try:
        with open("src/main.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        registrations = []
        lines = content.split('\n')
        
        for line in lines:
            if "app.include_router(" in line:
                registrations.append(line.strip())
        
        return registrations
    except Exception as e:
        print(f"Error reading main.py: {e}")
        return []

def main():
    """Función principal"""
    print("🔍 VokaFlow Router Identifier v1.0")
    print("📊 Analizando todos los routers disponibles...")
    print("=" * 80)
    
    # Analizar directorio de routers
    routers_dir = Path("src/backend/routers")
    router_files = list(routers_dir.glob("*.py"))
    router_files = [f for f in router_files if f.name != "__init__.py" and not f.name.endswith("backup")]
    
    print(f"📁 Encontrados {len(router_files)} archivos de router")
    print()
    
    # Analizar cada router
    routers_info = {}
    
    for router_file in sorted(router_files):
        router_name = router_file.stem
        print(f"🔍 Analizando {router_name}...")
        
        info = analyze_router_file(str(router_file))
        routers_info[router_name] = info
    
    # Obtener información de main.py
    imports_from_main = get_router_imports_from_main()
    registrations_from_main = get_router_registrations_from_main()
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE ROUTERS DISPONIBLES")
    print("=" * 80)
    
    # Estadísticas generales
    total_routers = len(routers_info)
    active_routers = len([r for r in routers_info.values() if r.get("status") == "active"])
    configured_routers = len([r for r in routers_info.values() if r.get("status") == "configured"])
    inactive_routers = len([r for r in routers_info.values() if r.get("status") in ["inactive", "error"]])
    total_endpoints = sum(len(r.get("endpoints", [])) for r in routers_info.values())
    
    print(f"📈 Total de routers: {total_routers}")
    print(f"✅ Routers activos: {active_routers}")
    print(f"⚙️  Routers configurados: {configured_routers}")
    print(f"❌ Routers inactivos: {inactive_routers}")
    print(f"🎯 Total de endpoints: {total_endpoints}")
    print(f"📝 Importaciones en main.py: {len(imports_from_main)}")
    print(f"🔗 Registros en main.py: {len(registrations_from_main)}")
    
    print("\n" + "=" * 80)
    print("🎯 ROUTERS ACTIVOS (con endpoints)")
    print("=" * 80)
    
    for name, info in routers_info.items():
        if info.get("status") == "active":
            endpoint_count = len(info.get("endpoints", []))
            file_size_kb = info.get("file_size", 0) / 1024
            print(f"✅ {name:<20} | {endpoint_count:>3} endpoints | {file_size_kb:>6.1f}KB | {info.get('description', 'Sin descripción')[:50]}")
    
    print("\n" + "=" * 80)
    print("⚙️  ROUTERS CONFIGURADOS (sin endpoints)")
    print("=" * 80)
    
    for name, info in routers_info.items():
        if info.get("status") == "configured":
            file_size_kb = info.get("file_size", 0) / 1024
            print(f"⚙️  {name:<20} | {file_size_kb:>6.1f}KB | {info.get('description', 'Sin descripción')[:50]}")
    
    if inactive_routers > 0:
        print("\n" + "=" * 80)
        print("❌ ROUTERS INACTIVOS/CON ERRORES")
        print("=" * 80)
        
        for name, info in routers_info.items():
            if info.get("status") in ["inactive", "error"]:
                error_msg = info.get("error", "Sin router configurado")
                print(f"❌ {name:<20} | Error: {error_msg}")
    
    # Mostrar detalles de endpoints por router
    print("\n" + "=" * 80)
    print("📋 DETALLE DE ENDPOINTS POR ROUTER")
    print("=" * 80)
    
    for name, info in sorted(routers_info.items()):
        if info.get("status") == "active" and info.get("endpoints"):
            print(f"\n🔧 {name.upper()} ({len(info['endpoints'])} endpoints):")
            print("-" * 60)
            
            for endpoint in info["endpoints"][:10]:  # Mostrar primeros 10
                method = endpoint.get("method", "?")
                path = endpoint.get("path", "?")
                func = endpoint.get("function", "?")
                print(f"  {method:<6} {path:<30} → {func}")
            
            if len(info["endpoints"]) > 10:
                remaining = len(info["endpoints"]) - 10
                print(f"  ... y {remaining} endpoints más")
    
    # Verificar importaciones vs archivos existentes
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN DE IMPORTACIONES")
    print("=" * 80)
    
    imported_routers = set(imp["module"] for imp in imports_from_main)
    existing_routers = set(routers_info.keys())
    
    missing_imports = existing_routers - imported_routers
    missing_files = imported_routers - existing_routers
    
    if missing_imports:
        print("⚠️  Routers existentes NO importados en main.py:")
        for router in sorted(missing_imports):
            print(f"   - {router}")
    
    if missing_files:
        print("❌ Routers importados pero archivo NO existe:")
        for router in sorted(missing_files):
            print(f"   - {router}")
    
    if not missing_imports and not missing_files:
        print("✅ Todas las importaciones coinciden con archivos existentes")
    
    # Guardar resultados detallados
    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "analysis_timestamp": timestamp,
        "summary": {
            "total_routers": total_routers,
            "active_routers": active_routers,
            "configured_routers": configured_routers,
            "inactive_routers": inactive_routers,
            "total_endpoints": total_endpoints
        },
        "routers": routers_info,
        "imports_from_main": imports_from_main,
        "registrations_from_main": registrations_from_main,
        "missing_imports": list(missing_imports),
        "missing_files": list(missing_files)
    }
    
    filename = f"vokaflow_routers_analysis_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Análisis completo guardado en: {filename}")
    print(f"🎉 Análisis completado: {active_routers}/{total_routers} routers activos")

if __name__ == "__main__":
    main() 