import 'package:flutter/material.dart';

import '../../core/design/codo_colors.dart';
import '../../core/widgets/codo_logo.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const items = [
      ('Comprendre', 'Décrivez votre situation avec vos propres mots.', Icons.chat_bubble_outline_rounded),
      ('Vérifier', 'Chaque information importante renvoie vers sa source, sa version et son statut.', Icons.verified_outlined),
      ('Agir', 'Suivez les étapes documentées d’une procédure et identifiez l’autorité concernée.', Icons.route_outlined),
    ];
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Le droit ivoirien, accessible à tous.', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 28),
          ...items.map((item) => Container(
                margin: const EdgeInsets.only(bottom: 14),
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: CodoColors.pureSurface,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: CodoColors.quietBorder),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(item.$3, color: CodoColors.civicGreen),
                    const SizedBox(width: 14),
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text(item.$1, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
                      const SizedBox(height: 6),
                      Text(item.$2),
                    ])),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}
