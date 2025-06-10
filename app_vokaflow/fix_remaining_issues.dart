// Script to fix remaining compilation issues
// Run with: dart run fix_remaining_issues.dart

import 'dart:io';

void main() async {
  print('Starting to fix remaining compilation issues...');
  
  final libDir = Directory('lib');
  if (!libDir.existsSync()) {
    print('Error: lib directory not found');
    return;
  }

  // Fix specific files with targeted fixes
  await fixEstadosPageVokaColors();
  await fixAppInputHintText();
  await fixAppDropdownMenuTypeArgs();
  await fixMissingVokaColorsImports();
  await fixColorConstants();
  
  print('All remaining issues fixed!');
}

Future<void> fixEstadosPageVokaColors() async {
  final file = File('lib/features/estados/pages/estados_page.dart');
  if (!file.existsSync()) return;
  
  String content = await file.readAsString();
  
  // Replace VokaColors with AppColors or Colors
  content = content.replaceAll('VokaColors.card', 'AppColors.card');
  content = content.replaceAll('VokaColors.estados', 'AppColors.primary');
  content = content.replaceAll('VokaColors.surface', 'AppColors.surface');
  content = content.replaceAll('VokaColors.textPrimary', 'AppColors.primaryText');
  content = content.replaceAll('VokaColors.textSecondary', 'AppColors.secondaryText');
  content = content.replaceAll('VokaColors.textMuted', 'AppColors.mutedText');
  content = content.replaceAll('VokaColors.success', 'AppColors.success');
  content = content.replaceAll('VokaColors.translator', 'AppColors.accent');
  content = content.replaceAll('VokaColors.chat', 'AppColors.info');
  content = content.replaceAll('VokaColors.vicky', 'AppColors.warning');
  content = content.replaceAll('VokaColors.polyflow', 'AppColors.error');
  content = content.replaceAll('VokaColors.border', 'AppColors.border');
  content = content.replaceAll('VokaColors.primary', 'AppColors.primary');
  
  // Add missing import
  if (!content.contains("import '../../../core/constants/colors.dart';")) {
    content = content.replaceFirst(
      "import 'package:flutter/material.dart';",
      "import 'package:flutter/material.dart';\nimport '../../../core/constants/colors.dart';"
    );
  }
  
  await file.writeAsString(content);
  print('Fixed VokaColors references in estados_page.dart');
}

Future<void> fixAppInputHintText() async {
  final files = [
    'lib/features/document/pages/smart_document_page.dart',
    'lib/features/enterprise/pages/admin_panel_page.dart',
    'lib/features/enterprise/pages/integration_hub_page.dart',
    'lib/features/meeting/pages/ai_meeting_page.dart',
    'lib/features/teams/pages/teams_page.dart',
  ];
  
  for (final filePath in files) {
    final file = File(filePath);
    if (!file.existsSync()) continue;
    
    String content = await file.readAsString();
    
    // Replace hintText parameter with placeholder
    content = content.replaceAll('hintText:', 'placeholder:');
    
    await file.writeAsString(content);
  }
  
  print('Fixed AppInput hintText parameters');
}

Future<void> fixAppDropdownMenuTypeArgs() async {
  final files = [
    'lib/features/enterprise/pages/admin_panel_page.dart',
    'lib/features/enterprise/pages/integration_hub_page.dart',
  ];
  
  for (final filePath in files) {
    final file = File(filePath);
    if (!file.existsSync()) continue;
    
    String content = await file.readAsString();
    
    // Remove type arguments from AppDropdownMenu
    content = content.replaceAll(RegExp(r'AppDropdownMenu<[^>]+>'), 'AppDropdownMenu');
    
    // Fix DropdownMenuItem to use correct structure
    content = content.replaceAll('child: Text(', 'text: ');
    content = content.replaceAll(RegExp(r'DropdownMenuItem<[^>]+>\(\s*value:\s*([^,]+),\s*child:\s*([^)]+)\)'), 
                                'DropdownMenuItem(value: \$1, text: \$2)');
    
    await file.writeAsString(content);
  }
  
  print('Fixed AppDropdownMenu type arguments');
}

Future<void> fixMissingVokaColorsImports() async {
  final files = await Directory('lib').listSync(recursive: true);
  
  for (final file in files) {
    if (file is File && file.path.endsWith('.dart')) {
      String content = await file.readAsString();
      
      // If file uses VokaColors but doesn't import it, add the import
      if (content.contains('VokaColors.') && 
          !content.contains("import '../../../core/constants/voka_colors.dart';") &&
          !content.contains("import '../../constants/voka_colors.dart';") &&
          !content.contains("import '../constants/voka_colors.dart';")) {
        
        // Determine relative path based on file location
        String relativePath = '../../../core/constants/voka_colors.dart';
        if (file.path.contains('lib/core/')) {
          relativePath = '../constants/voka_colors.dart';
        } else if (file.path.contains('lib/presentation/')) {
          relativePath = '../../core/constants/voka_colors.dart';
        }
        
        content = content.replaceFirst(
          "import 'package:flutter/material.dart';",
          "import 'package:flutter/material.dart';\nimport '$relativePath';"
        );
        
        await file.writeAsString(content);
      }
    }
  }
  
  print('Fixed missing VokaColors imports');
}

Future<void> fixColorConstants() async {
  // Fix deprecated color constants
  final files = [
    'lib/app.dart',
    'lib/core/constants/colors.dart',
    'lib/core/constants/typography.dart',
  ];
  
  for (final filePath in files) {
    final file = File(filePath);
    if (!file.existsSync()) continue;
    
    String content = await file.readAsString();
    
    // Replace deprecated background/onBackground
    content = content.replaceAll('background:', 'surface:');
    content = content.replaceAll('onBackground:', 'onSurface:');
    
    await file.writeAsString(content);
  }
  
  print('Fixed deprecated color constants');
}
