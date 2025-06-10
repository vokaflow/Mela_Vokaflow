// Script para reparar errores críticos de sintaxis
// Run with: dart run fix_critical_syntax.dart

import 'dart:io';

void main() async {
  print('🔧 Reparando errores críticos de sintaxis...');
  
  // Paso 1: Arreglar argumentos duplicados
  await fixDuplicateArguments();
  
  // Paso 2: Crear archivo faltante crítico
  await createMissingEnterpriseService();
  
  // Paso 3: Arreglar VokaColors.border
  await fixVokaColorsBorder();
  
  // Paso 4: Arreglar parámetros de AppInput
  await fixAppInputParameters();
  
  print('✅ Errores críticos de sintaxis reparados');
}

Future<void> fixDuplicateArguments() async {
  print('📝 Arreglando argumentos duplicados...');
  
  // app.dart
  final appFile = File('lib/app.dart');
  if (appFile.existsSync()) {
    String content = await appFile.readAsString();
    
    // Eliminar la línea duplicada de surface
    content = content.replaceAll(
      RegExp(r'surface: AppColors\.cardBackground,\s*\n\s*surface: AppColors\.surface,'),
      'surface: AppColors.surface,'
    );
    
    // Eliminar la línea duplicada de onSurface  
    content = content.replaceAll(
      RegExp(r'onSurface: AppColors\.primaryText,\s*\n\s*onSurface: AppColors\.primaryText,'),
      'onSurface: AppColors.primaryText,'
    );
    
    await appFile.writeAsString(content);
  }
  
  // colors.dart
  final colorsFile = File('lib/core/constants/colors.dart');
  if (colorsFile.existsSync()) {
    String content = await colorsFile.readAsString();
    
    content = content.replaceAll(
      RegExp(r'surface: background,\s*\n\s*onSurface: textPrimary,'),
      'surface: background,'
    );
    
    await colorsFile.writeAsString(content);
  }
  
  // typography.dart
  final typographyFile = File('lib/core/constants/typography.dart');
  if (typographyFile.existsSync()) {
    String content = await typographyFile.readAsString();
    
    content = content.replaceAll(
      RegExp(r'surface: AppColors\.fondoOscuroPrincipal,\s*\n.*onSurface: AppColors\.textoPrincipal,'),
      'surface: AppColors.fondoOscuroPrincipal,'
    );
    
    await typographyFile.writeAsString(content);
  }
  
  print('  ✅ Argumentos duplicados eliminados');
}

Future<void> createMissingEnterpriseService() async {
  print('📝 Creando enterprise_service.dart faltante...');
  
  final file = File('lib/core/services/enterprise/enterprise_service.dart');
  
  await file.writeAsString('''
import 'package:flutter/foundation.dart';

/// Servicio principal para funcionalidades enterprise
class EnterpriseService {
  static final EnterpriseService _instance = EnterpriseService._internal();
  factory EnterpriseService() => _instance;
  EnterpriseService._internal();

  bool _isEnterpriseEnabled = false;
  String? _licenseKey;
  
  /// Inicializa el servicio enterprise
  Future<void> initialize({String? licenseKey}) async {
    _licenseKey = licenseKey;
    _isEnterpriseEnabled = licenseKey != null && licenseKey.isNotEmpty;
    
    if (kDebugMode) {
      print('EnterpriseService initialized: enabled=\$_isEnterpriseEnabled');
    }
  }
  
  /// Verifica si las funcionalidades enterprise están habilitadas
  bool get isEnterpriseEnabled => _isEnterpriseEnabled;
  
  /// Obtiene la clave de licencia actual
  String? get licenseKey => _licenseKey;
  
  /// Valida una funcionalidad enterprise específica
  bool isFeatureEnabled(String feature) {
    if (!_isEnterpriseEnabled) return false;
    
    // Por ahora todas las features están habilitadas si enterprise está activo
    return true;
  }
  
  /// Lista de funcionalidades enterprise disponibles
  List<String> get availableFeatures => [
    'advanced_analytics',
    'team_management', 
    'sso_integration',
    'audit_logging',
    'advanced_security',
    'multi_tenant',
    'ai_workflows',
  ];
}
''');
  
  print('  ✅ enterprise_service.dart creado');
}

Future<void> fixVokaColorsBorder() async {
  print('📝 Arreglando VokaColors.border...');
  
  final file = File('lib/core/widgets/enterprise/settings_widgets.dart');
  if (file.existsSync()) {
    String content = await file.readAsString();
    
    // Reemplazar VokaColors.border con AppColors.border
    content = content.replaceAll('VokaColors.border', 'AppColors.border');
    
    await file.writeAsString(content);
  }
  
  print('  ✅ VokaColors.border reemplazado');
}

Future<void> fixAppInputParameters() async {
  print('📝 Arreglando parámetros de AppInput...');
  
  final files = [
    'lib/features/document/pages/smart_document_page.dart',
    'lib/features/meeting/pages/ai_meeting_page.dart', 
    'lib/features/teams/pages/teams_page.dart',
    'lib/features/enterprise/pages/admin_panel_page.dart',
    'lib/features/enterprise/pages/integration_hub_page.dart',
  ];
  
  for (final filePath in files) {
    final file = File(filePath);
    if (file.existsSync()) {
      String content = await file.readAsString();
      
      // Cambiar placeholder: por hintText:
      content = content.replaceAll('placeholder:', 'hintText:');
      
      await file.writeAsString(content);
    }
  }
  
  print('  ✅ Parámetros de AppInput corregidos');
}
