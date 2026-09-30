import 'package:flutter/material.dart';

import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';

class ProScreen extends StatelessWidget {
  const ProScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('CODO Pro', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Recherche documentaire avancée pour juristes, étudiants, chercheurs, entreprises, directions juridiques et administrations.', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 20),
          FilledButton.icon(
            onPressed: () => Navigator.pushNamed(context, CodoRoutes.proAdvanced),
            icon: const Icon(Icons.tune_rounded),
            label: const Text('Recherche avancée'),
          ),
          const SizedBox(height: 24),
          const CodoEmptyState(
            title: 'Espace professionnel en construction',
            message: 'Comparaison de textes, recherche par période, référence, dossiers documentaires et historique législatif seront alimentés par le même corpus vérifié.',
            icon: Icons.work_outline_rounded,
          ),
        ],
      ),
    );
  }
}
