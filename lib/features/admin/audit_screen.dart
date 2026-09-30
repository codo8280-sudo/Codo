import 'package:flutter/material.dart';

import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';

class AuditScreen extends StatelessWidget {
  const AuditScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const CodoLogo(compact: true)),
        body: ListView(padding: const EdgeInsets.all(20), children: [
          Text('Audit et traçabilité', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Qui a fait quoi, sur quelle entité, quand, et avec quel état avant / après.', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 24),
          const CodoEmptyState(title: 'Journal prêt à être alimenté', message: 'Les événements administratifs seront append-only et consultables par les rôles autorisés.', icon: Icons.manage_search_rounded),
        ]),
      );
}
