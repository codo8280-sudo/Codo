import 'package:flutter/material.dart';

import '../../core/widgets/codo_logo.dart';

class ImportTextScreen extends StatelessWidget {
  const ImportTextScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Import d’un nouveau texte', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 24),
          const TextField(decoration: InputDecoration(labelText: 'Source institutionnelle')),
          const SizedBox(height: 14),
          const TextField(decoration: InputDecoration(labelText: 'URL officielle')),
          const SizedBox(height: 14),
          const TextField(decoration: InputDecoration(labelText: 'Nature du texte')),
          const SizedBox(height: 14),
          const TextField(decoration: InputDecoration(labelText: 'Référence / numéro')),
          const SizedBox(height: 14),
          const TextField(maxLines: 4, decoration: InputDecoration(labelText: 'Notes d’acquisition')),
          const SizedBox(height: 20),
          FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.upload_file_outlined), label: const Text('Créer le dossier d’import')),
          const SizedBox(height: 12),
          Text('Workflow : Importé → À analyser → Structuré → Sources vérifiées → Contrôle juridique → Validé → Publié → Surveillé.', style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}
