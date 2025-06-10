import 'dart:io';

void main() async {
  print('🔧 Corrigiendo nombres de widgets en todos los archivos...');
  
  final filesToFix = [
    'lib/features/teams/pages/teams_page.dart',
    'lib/features/meeting/pages/ai_meeting_page.dart',
    'lib/features/document/pages/smart_document_page.dart',
    'lib/core/widgets/enterprise/settings_widgets.dart',
  ];
  
  for (final filePath in filesToFix) {
    final file = File(filePath);
    if (await file.exists()) {
      print('Corrigiendo $filePath...');
      String content = await file.readAsString();
      
      // Correcciones de widgets
      content = content.replaceAll('AppCard(', 'VokaCard(');
      content = content.replaceAll('AppInput(', 'VokaInput(');
      content = content.replaceAll('AppSkeleton(', 'VokaSkeleton(');
      content = content.replaceAll('AppDropdownMenu(', 'VokaDropdownMenu(');
      content = content.replaceAll('AppDropdownMenuItem(', 'VokaDropdownItem(');
      
      // Correcciones de parámetros
      content = content.replaceAll('hintText:', 'hint:');
      
      await file.writeAsString(content);
      print('✅ $filePath corregido!');
    }
  }
  
  print('🎉 Todos los archivos han sido corregidos!');
}
