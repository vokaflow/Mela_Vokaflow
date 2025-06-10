import 'dart:io';

void main() async {
  print('🔥 OPERACIÓN FÉNIX - FASE 3: CIRUGÍA DE SINTAXIS CRÍTICA');
  
  final file = File('lib/features/enterprise/pages/integration_hub_page.dart');
  if (!await file.exists()) {
    print('❌ Archivo no encontrado');
    return;
  }
  
  String content = await file.readAsString();
  
  // Corrección 1: Parámetros de widgets - corregir 'text:' en botones
  content = content.replaceAll(
    RegExp(r'TextButton\(\s*onPressed:\s*([^,]+),\s*child:\s*Text\(\s*text:\s*([^)]+)\)\s*\)'),
    'TextButton(onPressed: \$1, child: Text(\$2))'
  );
  
  content = content.replaceAll(
    RegExp(r'ElevatedButton\(\s*onPressed:\s*([^,]+),\s*child:\s*Text\(\s*text:\s*([^)]+)\)\s*\)'),
    'ElevatedButton(onPressed: \$1, child: Text(\$2))'
  );
  
  // Corrección 2: showDialog con parámetros correctos
  content = content.replaceAll(
    'showDialog(',
    'showDialog(\n      context: context,'
  );
  
  // Corrección 3: Corregir parámetros incorrectos en widgets
  content = content.replaceAll('conchild:', 'child:');
  content = content.replaceAll('text:', 'child: Text(');
  
  // Corrección 4: Corregir VokaInput hint
  content = content.replaceAll('hint: \'Buscar en logs...\'', 'hint: \'Buscar en logs...\'');
  
  await file.writeAsString(content);
  print('✅ Cirugía de sintaxis completada en integration_hub_page.dart');
  print('🎉 FASE 3 COMPLETADA!');
}
