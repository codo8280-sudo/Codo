import 'package:flutter/material.dart';

import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';

class CodeExplorerScreen extends StatelessWidget {
  const CodeExplorerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Explorateur d’un texte', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Corpus → Livre → Titre → Chapitre → Section → Article', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 24),
          const CodoEmptyState(
            title: 'Aucun texte sélectionné',
            message: 'L’explorateur n’affichera une structure juridique qu’après ingestion et validation d’une version officielle.',
          ),
          const SizedBox(height: 20),
          OutlinedButton.icon(
            onPressed: () => Navigator.pushNamed(context, CodoRoutes.article),
            icon: const Icon(Icons.article_outlined),
            label: const Text('Prévisualiser la fiche article'),
          ),
        ],
      ),
    );
  }
}
