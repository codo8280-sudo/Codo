import 'package:flutter/material.dart';

import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/source_required_card.dart';

class ProAdvancedSearchScreen extends StatelessWidget {
  const ProAdvancedSearchScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const filters = ['Nature', 'Numéro', 'Date', 'Domaine', 'Statut', 'Institution', 'Juridiction', 'Texte cité'];
    return Scaffold(
      appBar: AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Recherche avancée CODO Pro', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 20),
          const TextField(decoration: InputDecoration(labelText: 'Requête', hintText: 'Référence, expression ou termes juridiques')),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: filters.map((f) => FilterChip(label: Text(f), selected: false, onSelected: (_) {})).toList(),
          ),
          const SizedBox(height: 20),
          const SourceRequiredCard(detail: 'La recherche multicritère sera exécutée sur le corpus indexé et versionné, jamais sur des données simulées.'),
        ],
      ),
    );
  }
}
