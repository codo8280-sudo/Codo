import 'package:flutter/material.dart';

import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';

class JurisprudenceScreen extends StatelessWidget {
  const JurisprudenceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Jurisprudence', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text('Juridiction, date, numéro, matière, question juridique, textes cités et source.', style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 20),
          const TextField(decoration: InputDecoration(prefixIcon: Icon(Icons.search_rounded), hintText: 'Rechercher une décision')),
          const SizedBox(height: 24),
          const CodoEmptyState(
            title: 'Aucune décision indexée dans cette fondation',
            message: 'CODO différenciera toujours texte normatif, décision juridictionnelle et commentaire doctrinal.',
            icon: Icons.gavel_outlined,
          ),
          const SizedBox(height: 20),
          OutlinedButton(onPressed: () => Navigator.pushNamed(context, CodoRoutes.decisionDetail), child: const Text('Prévisualiser la structure d’une décision')),
        ],
      ),
    );
  }
}
