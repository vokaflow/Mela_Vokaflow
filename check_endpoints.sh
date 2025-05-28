#!/bin/bash
echo "🔍 ANÁLISIS DE ENDPOINTS VOKAFLOW"
echo "================================="
echo

total_endpoints=0

for file in src/backend/routers/*.py; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .py)
        echo "📁 Router: $filename"
        echo "-------------------"
        
        # Extraer endpoints del archivo
        endpoints=$(grep -n "@router\." "$file" | grep -E "(get|post|put|delete|patch)")
        count=$(echo "$endpoints" | wc -l)
        
        if [ "$count" -gt 0 ]; then
            echo "$endpoints" | while read line; do
                line_num=$(echo "$line" | cut -d: -f1)
                method=$(echo "$line" | grep -oE '(get|post|put|delete|patch)')
                route=$(echo "$line" | grep -oE '"[^"]*"' | tr -d '"')
                echo "  $method $route (línea $line_num)"
            done
            echo "  Total: $count endpoints"
            total_endpoints=$((total_endpoints + count))
        else
            echo "  No se encontraron endpoints"
        fi
        echo
    fi
done

echo "🎯 RESUMEN TOTAL: $total_endpoints endpoints encontrados"
