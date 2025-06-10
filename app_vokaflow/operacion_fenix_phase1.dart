import 'dart:io';

void main() async {
  print('🔥 OPERACIÓN FÉNIX - FASE 1: POPUP MENU ITEMS');
  
  // Lista de archivos con errores de PopupMenuItem
  final filesToFix = [
    'lib/features/enterprise/pages/integration_hub_page.dart',
    'lib/features/teams/pages/teams_page.dart',
    'lib/features/enterprise/pages/admin_panel_page.dart',
    'lib/features/meeting/pages/ai_meeting_page.dart',
    'lib/features/document/pages/smart_document_page.dart',
    'lib/features/chat/pages/chat_settings_page.dart',
    'lib/features/estados/pages/estados_settings_page.dart',
    'lib/features/translator/pages/translator_settings_page.dart',
    'lib/features/vicky/pages/vicky_settings_page.dart',
  ];
  
  for (final filePath in filesToFix) {
    final file = File(filePath);
    if (await file.exists()) {
      print('🎯 Corrigiendo PopupMenuItem en: $filePath');
      String content = await file.readAsString();
      
      // Corrección masiva de PopupMenuItem
      content = content.replaceAll(
        RegExp(r'PopupMenuItem\(\s*value:\s*([^,]+),\s*text:\s*([^)]+)\)'),
        'PopupMenuItem(value: \$1, child: Text(\$2))'
      );
      
      // Casos específicos adicionales
      content = content.replaceAll('text: \'Probar\')', 'child: Text(\'Probar\'))');
      content = content.replaceAll('text: \'Configurar\')', 'child: Text(\'Configurar\'))');
      content = content.replaceAll('text: \'Eliminar\'', 'child: Text(\'Eliminar\')');
      content = content.replaceAll('text: \'Cerrar\')', 'child: Text(\'Cerrar\'))');
      content = content.replaceAll('text: \'Cancelar\')', 'child: Text(\'Cancelar\'))');
      content = content.replaceAll('text: \'Instalar\')', 'child: Text(\'Instalar\'))');
      content = content.replaceAll('text: \'Ir al Marketplace\')', 'child: Text(\'Ir al Marketplace\'))');
      
      await file.writeAsString(content);
      print('✅ PopupMenuItem corregido en: $filePath');
    }
  }
  
  print('🎉 FASE 1 COMPLETADA - PopupMenuItem corregidos!');
}
