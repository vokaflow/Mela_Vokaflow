// Script to fix withOpacity deprecation issues across the project
// Run with: dart run fix_withopacity_issues.dart

import 'dart:io';

void main() async {
  print('Starting to fix withOpacity deprecation issues...');
  
  final libDir = Directory('lib');
  if (!libDir.existsSync()) {
    print('Error: lib directory not found');
    return;
  }

  await fixWithOpacityInDirectory(libDir);
  print('All withOpacity issues fixed!');
}

Future<void> fixWithOpacityInDirectory(Directory dir) async {
  final files = dir.listSync(recursive: true);
  
  for (final file in files) {
    if (file is File && file.path.endsWith('.dart')) {
      await fixWithOpacityInFile(file);
    }
  }
}

Future<void> fixWithOpacityInFile(File file) async {
  try {
    String content = await file.readAsString();
    String originalContent = content;
    
    // Replace all withOpacity(alpha) patterns with withValues(alpha: alpha)
    final regex = RegExp(r'\.withOpacity\(([^)]+)\)');
    content = content.replaceAllMapped(regex, (match) {
      final alphaValue = match.group(1)!;
      return '.withValues(alpha: $alphaValue)';
    });
    
    // Only write if content changed
    if (content != originalContent) {
      await file.writeAsString(content);
      print('Fixed withOpacity in: ${file.path}');
    }
  } catch (e) {
    print('Error fixing file ${file.path}: $e');
  }
}
