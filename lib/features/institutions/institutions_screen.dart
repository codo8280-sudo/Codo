import 'package:flutter/material.dart';

import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';

class InstitutionsScreen extends StatelessWidget {
  const InstitutionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Institutions', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Trouver une juridiction ou une administration.', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 20),
          const TextField(decoration: InputDecoration(prefixIcon: Icon(Icons.search_rounded), hintText: 'Nom, compétence ou procédure')),
          const SizedBox(height: 24),
          const CodoEmptyState(
            title: 'Annuaire à valider',
            message: 'Adresse, contacts, horaires et compétences ne seront publiés qu’avec une provenance officielle.',
            icon: Icons.account_balance_outlined,
          ),
          const SizedBox(height: 20),
          OutlinedButton(onPressed: () => Navigator.pushNamed(context, CodoRoutes.institutionDetail), child: const Text('Prévisualiser une fiche institution')),
        ],
      ),
    );
  }
}
