import 'package:flutter/material.dart';

import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';

class VersionCompareScreen extends StatelessWidget {
  const VersionCompareScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Comparer les versions', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Version précédente ↔ version actuelle', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 24),
          const CodoEmptyState(
            title: 'Sélectionnez deux versions vérifiées',
            message: 'Les différences seront présentées avec une hiérarchie neutre, sans palette multicolore excessive.',
            icon: Icons.compare_arrows_rounded,
          ),
        ],
      ),
    );
  }
}
