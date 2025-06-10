import 'dart:io';

void main() async {
  print('🔧 Corrigiendo errores restantes...');
  
  final file = File('lib/features/enterprise/pages/integration_hub_page.dart');
  String content = await file.readAsString();
  
  // Corregir VokaDropdownMenuItem a VokaDropdownItem
  content = content.replaceAll('VokaDropdownMenuItem(', 'VokaDropdownItem(');
  content = content.replaceAll('text:', 'label:');
  
  // Corregir problemas específicos de widgets mal estructurados
  content = content.replaceAll(
    RegExp(r'Expanded\(\s*child:\s*Text\(\s*integration\.name,'),
    'Expanded(\n              child: Text(\n                integration.name,'
  );
  
  content = content.replaceAll(
    RegExp(r'Container\(\s*padding:[^}]+\},\s*child:\s*Text\(\s*_getStatusDisplayName'),
    'Container(\n              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),\n              decoration: BoxDecoration(\n                color: statusColor.withValues(alpha: 0.1),\n                borderRadius: BorderRadius.circular(12),\n                border: Border.all(color: statusColor.withValues(alpha: 0.3)),\n              ),\n              child: Text(\n                _getStatusDisplayName'
  );
  
  // Corregir problemas de SizedBox
  content = content.replaceAll(
    RegExp(r'SizedBox\(\s*width:\s*80,\s*child:\s*Text\(\s*\'\\\$label:\','),
    r'SizedBox(\n            width: 80,\n            child: Text(\n              \'\$label:\','
  );
  
  // Corregir problemas de Container con child: Text mal estructurado
  content = content.replaceAll(
    RegExp(r'Container\(\s*padding:[^}]+\},\s*child:\s*Text\(\s*integration\.name,'),
    'Container(\n              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),\n              decoration: BoxDecoration(\n                color: actionColor.withValues(alpha: 0.1),\n                borderRadius: BorderRadius.circular(8),\n              ),\n              child: Text(\n                integration.name,'
  );
  
  await file.writeAsString(content);
  print('✅ Errores restantes corregidos!');
}
