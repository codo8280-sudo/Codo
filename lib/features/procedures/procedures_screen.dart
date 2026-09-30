import 'package:flutter/material.dart';

import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_logo.dart';

class ProceduresScreen extends StatelessWidget {
  const ProceduresScreen({super.key});

  static const procedures = [
    'Dépôt de plainte', 'Procédure pénale', 'Garde à vue', 'Convocation', 'Recours', 'Recouvrement de créances', 'Litiges locatifs', 'Conflits fonciers', 'Succession', 'Divorce', 'État civil', 'Droit du travail', 'Licenciement', 'Création et fonctionnement des entreprises', 'Contentieux commerciaux', 'Construction et urbanisme', 'Fiscalité', 'Contentieux administratif', 'Marchés publics', 'Consommation', 'Assurances', 'Accidents de circulation',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const CodoLogo(compact: true)),
      body: ListView.separated(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        itemCount: procedures.length + 1,
        separatorBuilder: (_, __) => const Divider(),
        itemBuilder: (context, index) {
          if (index == 0) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('Procédures', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 8),
                Text('Chaque procédure est structurée en étapes et reliée à ses sources juridiques.', style: Theme.of(context).textTheme.bodySmall),
              ]),
            );
          }
          final title = procedures[index - 1];
          return ListTile(
            contentPadding: EdgeInsets.zero,
            title: Text(title),
            subtitle: const Text('Structure disponible ; contenu juridique soumis à validation du corpus'),
            trailing: const Icon(Icons.arrow_forward_rounded),
            onTap: () => Navigator.pushNamed(context, CodoRoutes.procedureDetail, arguments: title),
          );
        },
      ),
    );
  }
}
