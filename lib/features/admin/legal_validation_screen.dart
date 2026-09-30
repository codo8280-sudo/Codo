import 'package:flutter/material.dart';

import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/source_required_card.dart';

class LegalValidationScreen extends StatelessWidget {
  const LegalValidationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const checks = ['Source identifiée', 'Document original conservé', 'Numéro vérifié', 'Date vérifiée', 'Version vérifiée', 'Statut vérifié', 'Texte complet', 'Relations de modification vérifiées', 'Citations IA testées', 'Historique enregistré'];
    return Scaffold(
      appBar: AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Validation juridique', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Contrôle préalable à toute publication juridique.', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 20),
          ...checks.map((check) => CheckboxListTile(contentPadding: EdgeInsets.zero, value: false, onChanged: (_) {}, title: Text(check))),
          const SizedBox(height: 16),
          const SourceRequiredCard(detail: 'La publication reste impossible tant que les contrôles obligatoires ne sont pas satisfaits.'),
          const SizedBox(height: 20),
          Row(children: [
            Expanded(child: OutlinedButton(onPressed: () {}, child: const Text('Demander correction'))),
            const SizedBox(width: 10),
            Expanded(child: FilledButton(onPressed: () {}, child: const Text('Valider'))),
          ]),
        ],
      ),
    );
  }
}
