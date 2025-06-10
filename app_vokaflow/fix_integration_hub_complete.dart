import 'dart:io';

void main() async {
  print('🚀 Iniciando corrección completa del Integration Hub...');
  
  final file = File('lib/features/enterprise/pages/integration_hub_page.dart');
  String content = await file.readAsString();
  
  // Correcciones de widgets
  content = content.replaceAll('AppCard(', 'VokaCard(');
  content = content.replaceAll('AppInput(', 'VokaInput(');
  content = content.replaceAll('AppSkeleton(', 'VokaSkeleton(');
  content = content.replaceAll('AppDropdownMenu(', 'VokaDropdownMenu(');
  content = content.replaceAll('AppDropdownMenuItem(', 'VokaDropdownMenuItem(');
  
  // Correcciones de parámetros
  content = content.replaceAll('hintText:', 'hint:');
  content = content.replaceAll('text:', 'child:');
  
  // Correcciones de PopupMenuItem
  content = content.replaceAll('PopupMenuItem(value: \'test\', text: \'Probar\')', 
                               'PopupMenuItem(value: \'test\', child: Text(\'Probar\'))');
  content = content.replaceAll('PopupMenuItem(value: \'configure\', text: \'Configurar\')',
                               'PopupMenuItem(value: \'configure\', child: Text(\'Configurar\'))');
  content = content.replaceAll('PopupMenuItem(\n              value: \'toggle\',\n              text: integration.status == IntegrationStatus.active ? \'Desactivar\' : \'Activar\')',
                               'PopupMenuItem(\n              value: \'toggle\',\n              child: Text(integration.status == IntegrationStatus.active ? \'Desactivar\' : \'Activar\'))');
  content = content.replaceAll('PopupMenuItem(\n              value: \'delete\',\n              text: \'Eliminar\', style: TextStyle(color: Colors.red))',
                               'PopupMenuItem(\n              value: \'delete\',\n              child: Text(\'Eliminar\', style: TextStyle(color: Colors.red)))');
  
  // Correcciones de botones
  content = content.replaceAll('TextButton(\n            onPressed: () => Navigator.pop(context),\n            text: \'Cerrar\')',
                               'TextButton(\n            onPressed: () => Navigator.pop(context),\n            child: Text(\'Cerrar\'))');
  content = content.replaceAll('ElevatedButton(\n            onPressed: () {\n              Navigator.pop(context);\n              _tabController.animateTo(1); // Go to marketplace\n            },\n            text: \'Ir al Marketplace\')',
                               'ElevatedButton(\n            onPressed: () {\n              Navigator.pop(context);\n              _tabController.animateTo(1); // Go to marketplace\n            },\n            child: Text(\'Ir al Marketplace\'))');
  
  // Correcciones de showDialog
  content = content.replaceAll('showDialog(\n      context: context,\n      builder: (context) => AlertDialog(',
                               'showDialog<void>(\n      context: context,\n      builder: (context) => AlertDialog(');
  
  // Correcciones específicas de widgets mal estructurados
  content = content.replaceAll('child: Text(\n                  \'No hay actividad reciente\',',
                               'child: Text(\n                  \'No hay actividad reciente\',');
  
  // Correcciones de Container mal estructurado
  content = content.replaceAll('Container(\n                  width: double.infinity,\n                  padding: const EdgeInsets.all(12),\n                  decoration: BoxDecoration(\n                    color: AppColors.surfaceVariant,\n                    borderRadius: BorderRadius.circular(8),\n                  ),\n                  text:',
                               'Container(\n                  width: double.infinity,\n                  padding: const EdgeInsets.all(12),\n                  decoration: BoxDecoration(\n                    color: AppColors.surfaceVariant,\n                    borderRadius: BorderRadius.circular(8),\n                  ),\n                  child: Text(');
  
  await file.writeAsString(content);
  print('✅ Corrección completa del Integration Hub terminada!');
}
