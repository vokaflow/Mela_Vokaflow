// Script to fix import issues across the project
// Run with: dart run fix_import_issues.dart

import 'dart:io';

void main() async {
  print('Starting to fix import issues...');
  
  final libDir = Directory('lib');
  if (!libDir.existsSync()) {
    print('Error: lib directory not found');
    return;
  }

  await fixImportsInDirectory(libDir);
  print('All import issues fixed!');
}

Future<void> fixImportsInDirectory(Directory dir) async {
  final files = dir.listSync(recursive: true);
  
  for (final file in files) {
    if (file is File && file.path.endsWith('.dart')) {
      await fixImportsInFile(file);
    }
  }
}

Future<void> fixImportsInFile(File file) async {
  try {
    String content = await file.readAsString();
    String originalContent = content;
    bool changed = false;
    
    // Fix imports from presentation/widgets to core/widgets
    if (content.contains("import '../../../presentation/widgets/ui/card.dart';") ||
        content.contains("import '../../../presentation/widgets/ui/skeleton.dart';") ||
        content.contains("import '../../../presentation/widgets/ui/input.dart';") ||
        content.contains("import '../../../presentation/widgets/ui/button.dart';") ||
        content.contains("import '../../../presentation/widgets/ui/tabs.dart';") ||
        content.contains("import '../../../presentation/widgets/ui/dropdown_menu.dart';") ||
        content.contains("import '../../../presentation/widgets/layout/app_layout.dart';") ||
        content.contains("import '../../../presentation/widgets/enterprise/settings_widgets.dart';")) {
      
      // Remove all individual widget imports
      content = content.replaceAll(RegExp(r"import\s+'\.\.\/\.\.\/\.\.\/presentation\/widgets\/ui\/\w+\.dart';\s*\n"), '');
      content = content.replaceAll(RegExp(r"import\s+'\.\.\/\.\.\/\.\.\/presentation\/widgets\/layout\/\w+\.dart';\s*\n"), '');
      content = content.replaceAll(RegExp(r"import\s+'\.\.\/\.\.\/\.\.\/presentation\/widgets\/enterprise\/\w+\.dart';\s*\n"), '');
      
      // Add the core widgets import if not already present
      if (!content.contains("import '../../../core/widgets/widgets.dart';")) {
        // Find the imports section and add our import
        final importRegex = RegExp(r"(import\s+'package:flutter/material\.dart';\s*\n)");
        content = content.replaceAllMapped(importRegex, (match) => 
          "${match.group(1)}import '../../../core/widgets/widgets.dart';\n");
      }
      changed = true;
    }
    
    // Fix package:vokaflow imports to relative imports
    content = content.replaceAll("import 'package:vokaflow/presentation/widgets/layout/app_layout.dart';", 
                                "import '../../../core/widgets/widgets.dart';");
    content = content.replaceAll("import 'package:vokaflow/presentation/widgets/enterprise/settings_widgets.dart';", 
                                "import '../../../core/widgets/widgets.dart';");
    
    // Remove unused imports
    final unusedImports = [
      "import 'package:easy_localization/easy_localization.dart';",
      "import 'package:vokaflow/core/constants/colors.dart';",
      "import 'package:vokaflow/core/services/enterprise/error_service.dart';",
      "import 'package:vokaflow/core/services/enterprise/loading_service.dart';",
      "import 'package:vokaflow/core/services/enterprise/settings_service.dart';",
      "import 'package:vokaflow/core/services/camera_service.dart';",
      "import 'package:vokaflow/core/services/tts_service.dart';",
      "import 'package:vokaflow/core/services/voice_service.dart';",
      "import 'package:firebase_auth/firebase_auth.dart';",
      "import 'package:go_router/go_router.dart';",
      "import 'package:vokaflow/core/router/app_router.dart';",
    ];
    
    for (final unusedImport in unusedImports) {
      if (content.contains(unusedImport) && !_isImportUsed(content, unusedImport)) {
        content = content.replaceAll('$unusedImport\n', '');
        changed = true;
      }
    }
    
    // Only write if content changed
    if (changed && content != originalContent) {
      await file.writeAsString(content);
      print('Fixed imports in: ${file.path}');
    }
  } catch (e) {
    print('Error fixing file ${file.path}: $e');
  }
}

bool _isImportUsed(String content, String import) {
  // Simple check to see if import is actually used
  // This is a basic implementation, could be more sophisticated
  if (import.contains('easy_localization')) {
    return content.contains('.tr()') || content.contains('context.locale');
  }
  if (import.contains('firebase_auth')) {
    return content.contains('FirebaseAuth') || content.contains('User');
  }
  if (import.contains('go_router')) {
    return content.contains('context.go') || content.contains('GoRouter');
  }
  // Add more checks as needed
  return false;
}
