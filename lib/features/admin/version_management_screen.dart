import 'package:flutter/material.dart';

import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';

class VersionManagementScreen extends StatelessWidget {
  const VersionManagementScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: CodoLogo(compact: true)),
        body: ListView(padding: const EdgeInsets.all(20), children: [
          Text('Gestion des versions', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Répondre à « que dit la loi aujourd’hui ? » et « que disait-elle à une date donnée ? ».', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 24),
          const CodoEmptyState(title: 'Aucun texte sélectionné', message: 'Sélectionnez un document validé pour consulter son historique temporel.', icon: Icons.history_rounded),
        ]),
      );
}
