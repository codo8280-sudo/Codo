import 'package:flutter/material.dart';

import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/source_required_card.dart';

class LawsScreen extends StatelessWidget {
  const LawsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const domains = ['Constitution', 'Droit pénal', 'Procédure pénale', 'Travail', 'Foncier / immobilier', 'Construction', 'Famille', 'Droit commercial / OHADA', 'Recouvrement'];
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Lois & Codes', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Domaine → Corpus → Texte → Livre → Titre → Chapitre → Section → Article', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 24),
          Wrap(spacing: 8, runSpacing: 8, children: domains.map((d) => ActionChip(label: Text(d), onPressed: () => Navigator.pushNamed(context, CodoRoutes.codeExplorer))).toList()),
          const SizedBox(height: 24),
          const SourceRequiredCard(detail: 'Le corpus officiel doit être ingéré, versionné puis validé juridiquement avant affichage.'),
        ],
      ),
    );
  }
}
