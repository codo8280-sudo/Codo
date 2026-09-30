import 'package:flutter/material.dart';

import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/source_required_card.dart';

class DecisionDetailScreen extends StatelessWidget {
  const DecisionDetailScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const labels = ['Juridiction', 'Formation', 'Date', 'Numéro', 'Matière', 'Textes cités', 'Faits', 'Question juridique', 'Décision', 'Source'];
    return Scaffold(
      appBar: AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Détail d’une décision', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 24),
          ...labels.map((label) => Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(width: 120, child: Text(label, style: const TextStyle(fontWeight: FontWeight.w700))),
                    const Expanded(child: Text('À renseigner depuis une source juridictionnelle vérifiée.')),
                  ],
                ),
              )),
          const SizedBox(height: 16),
          const SourceRequiredCard(),
        ],
      ),
    );
  }
}
