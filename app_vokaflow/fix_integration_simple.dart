import 'dart:io';

void main() async {
  print('🔧 Corrigiendo errores simples...');
  
  final file = File('lib/features/enterprise/pages/integration_hub_page.dart');
  String content = await file.readAsString();
  
  // Correcciones simples
  content = content.replaceAll('VokaDropdownMenuItem(', 'VokaDropdownItem(');
  content = content.replaceAll('label:', 'label:');
  
  await file.writeAsString(content);
  print('✅ Errores simples corregidos!');
}
