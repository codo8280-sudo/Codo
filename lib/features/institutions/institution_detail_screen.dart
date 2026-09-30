import 'package:flutter/material.dart';

import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/source_required_card.dart';

class InstitutionDetailScreen extends StatelessWidget {
  const InstitutionDetailScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Fiche institution / juridiction', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 20),
          const _Row(label: 'Nom'),
          const _Row(label: 'Type'),
          const _Row(label: 'Compétences documentées'),
          const _Row(label: 'Adresse officielle'),
          const _Row(label: 'Contacts vérifiés'),
          const _Row(label: 'Site officiel'),
          const _Row(label: 'Procédures réalisables'),
          const SizedBox(height: 20),
          const SourceRequiredCard(),
        ],
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({required this.label});
  final String label;
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 4),
          const Text('À confirmer depuis la source officielle.'),
        ]),
      );
}
