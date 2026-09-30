import 'package:flutter/material.dart';

import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/codo_search_field.dart';
import '../../core/widgets/source_required_card.dart';

class SituationsScreen extends StatefulWidget {
  const SituationsScreen({super.key});

  @override
  State<SituationsScreen> createState() => _SituationsScreenState();
}

class _SituationsScreenState extends State<SituationsScreen> {
  String? selected;

  static const situations = [
    ('Travail', 'J ai ete licencie'),
    ('Famille', 'Je veux divorcer'),
    ('Logement', 'Mon proprietaire veut augmenter mon loyer'),
    ('Terrain', 'Deux personnes revendiquent la meme parcelle'),
    ('Police / Justice', 'J ai recu une convocation'),
    ('Entreprise', 'Un client refuse de payer'),
    ('Construction', 'Je veux construire une maison'),
    ('Route', 'J ai eu un accident'),
    ('Internet', 'Quelqu un utilise mes photos sans autorisation'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Que vous arrive-t-il ?', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 16),
          CodoSearchField(onSubmitted: (value) => setState(() => selected = value)),
          const SizedBox(height: 24),
          if (selected != null) ...[
            SourceRequiredCard(detail: 'Situation recue : "$selected". La qualification juridique doit provenir du moteur documentaire.'),
            const SizedBox(height: 24),
          ],
          ...situations.map((item) => Card(
                margin: const EdgeInsets.only(bottom: 10),
                child: ListTile(
                  title: Text(item.$1),
                  subtitle: Text(item.$2),
                  trailing: const Icon(Icons.arrow_forward_rounded),
                  onTap: () => setState(() => selected = item.$2),
                ),
              )),
        ],
      ),
    );
  }
}
