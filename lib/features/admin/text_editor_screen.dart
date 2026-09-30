import 'package:flutter/material.dart';

import '../../core/widgets/codo_logo.dart';

class LegalTextEditorScreen extends StatelessWidget {
  const LegalTextEditorScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Éditeur de texte juridique', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 20),
          const TextField(decoration: InputDecoration(labelText: 'Titre officiel')),
          const SizedBox(height: 14),
          const TextField(decoration: InputDecoration(labelText: 'Identifiant CODO')),
          const SizedBox(height: 14),
          const TextField(maxLines: 14, decoration: InputDecoration(labelText: 'Texte officiel structuré')),
          const SizedBox(height: 20),
          FilledButton(onPressed: () {}, child: const Text('Enregistrer comme brouillon')),
          const SizedBox(height: 10),
          Text('Aucune modification silencieuse d’un texte publié : une nouvelle version doit être créée et auditée.', style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}
