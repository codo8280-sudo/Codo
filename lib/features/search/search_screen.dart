import 'package:flutter/material.dart';

import '../../core/di/codo_services.dart';
import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/codo_search_field.dart';
import '../../core/widgets/legal_status_badge.dart';
import '../../core/widgets/source_required_card.dart';
import '../../domain/models/legal_models.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  String? query;
  bool loading = false;
  Object? error;
  List<LegalSearchResult> results = const [];

  Future<void> _search(String value) async {
    setState(() {
      query = value;
      loading = true;
      error = null;
      results = const [];
    });
    try {
      final data = await CodoServicesScope.of(context).legalCorpus.search(value);
      if (!mounted) return;
      setState(() => results = data);
    } catch (e) {
      if (!mounted) return;
      setState(() => error = e);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Recherche universelle', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text(
            'Mot-clé, numéro, article, domaine, date, procédure ou question naturelle.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 20),
          CodoSearchField(onSubmitted: _search),
          const SizedBox(height: 24),
          if (loading) const LinearProgressIndicator(),
          if (query == null) const _SearchHelp(),
          if (query != null && !loading) ...[
            Text('Résultats pour « $query »', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),
            if (error != null)
              const SourceRequiredCard(detail: 'La recherche n’a pas pu interroger le corpus configuré.')
            else if (results.isEmpty)
              const CodoEmptyState(
                title: 'Aucun résultat juridique vérifié',
                message: 'CODO ne remplit pas les résultats avec des contenus simulés. Vérifiez la connexion du corpus ou affinez la recherche.',
                icon: Icons.search_off_rounded,
              )
            else
              ...results.map((result) => _ResultCard(result: result)),
          ],
        ],
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  const _ResultCard({required this.result});

  final LegalSearchResult result;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: result.article == null
            ? null
            : () => Navigator.pushNamed(context, CodoRoutes.article, arguments: result.article!.codoId),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Expanded(child: Text(result.document.title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700))),
                const SizedBox(width: 8),
                LegalStatusBadge(status: result.document.status),
              ]),
              if (result.article != null) ...[
                const SizedBox(height: 8),
                Text(result.article!.label, style: const TextStyle(fontWeight: FontWeight.w700)),
              ],
              const SizedBox(height: 8),
              Text(result.snippet),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(child: Text(result.document.source.name, style: Theme.of(context).textTheme.bodySmall)),
                  Text(
                    switch (result.retrievalKind) {
                      'hybrid' => 'Recherche hybride',
                      'semantic' => 'Recherche sémantique',
                      _ => 'Recherche textuelle',
                    },
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SearchHelp extends StatelessWidget {
  const _SearchHelp();

  @override
  Widget build(BuildContext context) {
    return const Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Vous pouvez rechercher :', style: TextStyle(fontWeight: FontWeight.w700)),
        SizedBox(height: 12),
        Text('• Constitution, codes, lois, ordonnances, décrets et arrêtés'),
        Text('• Actes uniformes OHADA'),
        Text('• Procédures et institutions'),
        Text('• Articles et références précises'),
        Text('• Situations de la vie quotidienne'),
      ],
    );
  }
}
