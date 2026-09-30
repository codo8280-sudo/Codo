import 'package:flutter/material.dart';

import '../../core/widgets/codo_logo.dart';

class SourceManagementScreen extends StatelessWidget {
  const SourceManagementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const levels = [
      ('A', 'Source officielle primaire'),
      ('B', 'Reproduction institutionnelle'),
      ('C', 'Source secondaire vérifiée'),
      ('D', 'Source documentaire non vérifiée'),
    ];
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Gestion des sources', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Registre de provenance et niveau de confiance documentaire.', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 20),
          ...levels.map((e) => ListTile(contentPadding: EdgeInsets.zero, leading: CircleAvatar(child: Text(e.$1)), title: Text(e.$2))),
          const SizedBox(height: 20),
          FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.add_rounded), label: const Text('Ajouter une source')),
        ],
      ),
    );
  }
}
