import 'dart:io';

void main() async {
  print('🔥 OPERACIÓN FÉNIX - FASE 2: COMPLETAR MIGRACIÓN WIDGETS');
  
  // Lista de archivos que aún necesitan corrección
  final filesToFix = [
    'lib/features/enterprise/pages/ai_command_center_page.dart',
    'lib/features/teams/pages/teams_page.dart',
    'lib/features/meeting/pages/ai_meeting_page.dart',
    'lib/features/document/pages/smart_document_page.dart',
    'lib/features/enterprise/pages/integration_hub_page.dart',
    'lib/core/widgets/enterprise/settings_widgets.dart',
  ];
  
  for (final filePath in filesToFix) {
    final file = File(filePath);
    if (await file.exists()) {
      print('🎯 Corrigiendo widgets en: $filePath');
      String content = await file.readAsString();
      
      // Corrección final de widgets App → Voka
      content = content.replaceAll('AppCard(', 'VokaCard(');
      content = content.replaceAll('AppInput(', 'VokaInput(');
      content = content.replaceAll('AppSkeleton(', 'VokaSkeleton(');
      content = content.replaceAll('AppDropdownMenu(', 'VokaDropdownMenu(');
      content = content.replaceAll('AppDropdownMenuItem(', 'VokaDropdownItem(');
      
      // Corrección de parámetros hintText → hint
      content = content.replaceAll('hintText:', 'hint:');
      
      // Corrección de placeholder → hint (otro caso)
      content = content.replaceAll('placeholder:', 'hint:');
      
      await file.writeAsString(content);
      print('✅ Widgets corregidos en: $filePath');
    }
  }
  
  print('🎉 FASE 2 COMPLETADA - Migración de widgets finalizada!');
}
