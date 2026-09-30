import 'package:flutter/material.dart';

import '../../core/design/codo_colors.dart';
import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/action_tile.dart';
import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/codo_search_field.dart';
import '../../core/widgets/codo_section.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key, required this.onNavigate});

  final ValueChanged<int> onNavigate;

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverAppBar(
          pinned: true,
          title: const CodoLogo(compact: true),
          actions: [
            IconButton(
              tooltip: 'Catalogue CODO',
              onPressed: () => _showProjectModules(context),
              icon: const Icon(Icons.menu_rounded),
            ),
          ],
        ),
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 48),
          sliver: SliverList(
            delegate: SliverChildListDelegate([
              Text(
                'Centre d’Orientation du Droit et des Obligations',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: CodoColors.civicGreen,
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 14),
              Text(
                'Comprendre le droit.\nSavoir comment agir.',
                style: Theme.of(context).textTheme.displaySmall,
              ),
              const SizedBox(height: 16),
              Text(
                'Recherchez les textes applicables en Côte d’Ivoire, comprenez vos droits et accédez aux procédures correspondantes.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: CodoColors.secondaryGraphite,
                    ),
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: () => onNavigate(2),
                icon: const Icon(Icons.arrow_forward_rounded),
                label: const Text('Poser une question à CODO'),
              ),
              const SizedBox(height: 40),
              CodoSection(
                title: 'Recherche universelle',
                description: 'Question, loi, article, procédure ou situation courante.',
                child: CodoSearchField(onSubmitted: (_) => onNavigate(1)),
              ),
              const SizedBox(height: 40),
              CodoSection(
                title: 'Que voulez-vous faire ?',
                child: Column(
                  children: [
                    ActionTile(
                      emphasis: true,
                      icon: Icons.lightbulb_outline_rounded,
                      title: 'Comprendre une situation',
                      subtitle: 'Partez de ce qui vous arrive, sans connaître le vocabulaire juridique.',
                      onTap: () => Navigator.pushNamed(context, CodoRoutes.situations),
                    ),
                    const SizedBox(height: 12),
                    ActionTile(
                      icon: Icons.menu_book_outlined,
                      title: 'Consulter les lois',
                      subtitle: 'Explorez le corpus juridique et ses versions vérifiées.',
                      onTap: () => Navigator.pushNamed(context, CodoRoutes.laws),
                    ),
                    const SizedBox(height: 12),
                    ActionTile(
                      icon: Icons.route_outlined,
                      title: 'Suivre une procédure',
                      subtitle: 'Comprenez les étapes et les sources qui les fondent.',
                      onTap: () => onNavigate(3),
                    ),
                    const SizedBox(height: 12),
                    ActionTile(
                      icon: Icons.account_balance_outlined,
                      title: 'Trouver une institution',
                      subtitle: 'Identifiez une juridiction ou une administration à partir de données vérifiées.',
                      onTap: () => Navigator.pushNamed(context, CodoRoutes.institutions),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 40),
              const _DomainGrid(),
              const SizedBox(height: 40),
              const _SourceFirstPanel(),
            ]),
          ),
        ),
      ],
    );
  }

  void _showProjectModules(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (context) => const FractionallySizedBox(
        heightFactor: .84,
        child: _ModuleCatalog(),
      ),
    );
  }
}

class _DomainGrid extends StatelessWidget {
  const _DomainGrid();

  @override
  Widget build(BuildContext context) {
    const domains = [
      'Droit pénal',
      'Travail',
      'Famille',
      'Immobilier',
      'Construction',
      'Entreprises',
      'OHADA',
      'Fiscalité',
      'Numérique',
      'Consommation',
    ];
    return CodoSection(
      title: 'Domaines juridiques',
      description: 'Navigation documentaire. Le contenu est affiché uniquement après vérification de sa source et de son statut.',
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: domains.map((d) => Chip(label: Text(d))).toList(),
      ),
    );
  }
}

class _SourceFirstPanel extends StatelessWidget {
  const _SourceFirstPanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: CodoColors.pureSurface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: CodoColors.quietBorder),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.account_balance_outlined, color: CodoColors.civicGreen),
          SizedBox(height: 14),
          Text('Une question. Une règle. Une source. Une orientation.', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
          SizedBox(height: 10),
          Text('Chaque réponse juridique CODO doit permettre de retrouver le texte, l’article, la version, le statut, la date et la provenance documentaire.'),
        ],
      ),
    );
  }
}

class _ModuleCatalog extends StatelessWidget {
  const _ModuleCatalog();

  static const modules = [
    ('Lois & Codes', CodoRoutes.laws),
    ('Explorateur d’un code', CodoRoutes.codeExplorer),
    ('Page article de loi', CodoRoutes.article),
    ('Historique d’un article', CodoRoutes.articleHistory),
    ('Comparaison de versions', CodoRoutes.versionCompare),
    ('Situations de vie', CodoRoutes.situations),
    ('Jurisprudence', CodoRoutes.jurisprudence),
    ('Institutions', CodoRoutes.institutions),
    ('Actualité et veille juridique', CodoRoutes.monitoring),
    ('CODO Pro', CodoRoutes.pro),
    ('Recherche avancée CODO Pro', CodoRoutes.proAdvanced),
    ('Connexion / création de compte', CodoRoutes.auth),
    ('Onboarding', CodoRoutes.onboarding),
    ('Paramètres et accessibilité', CodoRoutes.accessibility),
    ('Back-office juridique', CodoRoutes.admin),
  ];

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
      itemCount: modules.length + 1,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, index) {
        if (index == 0) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 20),
            child: Text('Catalogue produit CODO', style: Theme.of(context).textTheme.headlineMedium),
          );
        }
        final item = modules[index - 1];
        return ListTile(
          contentPadding: EdgeInsets.zero,
          title: Text(item.$1),
          subtitle: const Text('Écran construit dans la fondation actuelle'),
          trailing: const Icon(Icons.chevron_right_rounded),
          onTap: () {
            Navigator.pop(context);
            Navigator.pushNamed(context, item.$2);
          },
        );
      },
    );
  }
}
