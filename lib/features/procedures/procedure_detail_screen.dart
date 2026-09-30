import 'package:flutter/material.dart';

import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/source_required_card.dart';

class ProcedureDetailScreen extends StatelessWidget {
  const ProcedureDetailScreen({super.key, this.title});

  final String? title;

  @override
  Widget build(BuildContext context) {
    const steps = [
      'Vérifier les conditions',
      'Réunir les documents',
      'Identifier l’autorité compétente',
      'Effectuer la démarche',
      'Suivre le dossier',
      'Exercer un recours si applicable',
    ];
    return Scaffold(
      appBar: AppBar(title: const CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text(title ?? 'Détail d’une procédure', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Parcours standard CODO. Le contenu juridique de chaque étape doit être sourcé.', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 24),
          ...steps.indexed.map((e) => _Step(index: e.$1 + 1, title: e.$2)),
          const SizedBox(height: 20),
          const SourceRequiredCard(detail: 'Conditions, délais, coûts, documents et autorité compétente restent bloqués sans source vérifiée.'),
        ],
      ),
    );
  }
}

class _Step extends StatelessWidget {
  const _Step({required this.index, required this.title});

  final int index;
  final String title;

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            width: 44,
            child: Column(
              children: [
                CircleAvatar(radius: 17, child: Text(index.toString().padLeft(2, '0'))),
                const Expanded(child: VerticalDivider()),
              ],
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(left: 10, bottom: 22),
              child: Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
            ),
          ),
        ],
      ),
    );
  }
}
