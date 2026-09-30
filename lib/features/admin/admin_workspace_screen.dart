import 'package:flutter/material.dart';

import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_logo.dart';

class AdminWorkspaceScreen extends StatelessWidget {
  const AdminWorkspaceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const entries = [
      ('Importer un texte', CodoRoutes.adminImport, Icons.upload_file_outlined),
      ('Validation juridique', CodoRoutes.adminValidation, Icons.fact_check_outlined),
      ('Éditeur de texte', CodoRoutes.adminEditor, Icons.edit_document),
      ('Gestion des versions', CodoRoutes.adminVersions, Icons.history_rounded),
      ('Gestion des sources', CodoRoutes.adminSources, Icons.source_outlined),
      ('Audit et traçabilité', CodoRoutes.adminAudit, Icons.manage_search_rounded),
    ];
    return Scaffold(
      appBar: AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Back-office juridique', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Poste de travail documentaire. Chaque action sensible doit être historisée.', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 20),
          ...entries.map((e) => ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Icon(e.$3),
                title: Text(e.$1),
                trailing: const Icon(Icons.chevron_right_rounded),
                onTap: () => Navigator.pushNamed(context, e.$2),
              )),
        ],
      ),
    );
  }
}
