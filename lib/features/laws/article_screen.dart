import 'package:flutter/material.dart';

import '../../core/di/codo_services.dart';
import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/legal_source_card.dart';
import '../../core/widgets/legal_status_badge.dart';
import '../../core/widgets/source_required_card.dart';
import '../../domain/models/legal_models.dart';

class ArticleScreen extends StatefulWidget {
  const ArticleScreen({super.key, this.codoId});

  final String? codoId;

  @override
  State<ArticleScreen> createState() => _ArticleScreenState();
}

class _ArticleScreenState extends State<ArticleScreen> {
  LegalArticle? article;
  DocumentProvenance? provenance;
  PublicationReceipt? publicationReceipt;
  List<LegalRelationship> relationships = const [];
  bool loading = false;
  bool savingFavorite = false;
  String? favoriteMessage;

  bool _requested = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_requested && widget.codoId != null) {
      _requested = true;
      _load();
    }
  }

  Future<void> _load() async {
    setState(() => loading = true);
    final repository = CodoServicesScope.of(context).legalCorpus;
    final result = await repository.articleById(widget.codoId!);
    DocumentProvenance? provenanceResult;
    PublicationReceipt? publicationReceiptResult;
    List<LegalRelationship> relationshipResult = const [];
    if (result != null && result.documentId.isNotEmpty) {
      provenanceResult = await repository.documentProvenance(result.documentId);
      publicationReceiptResult = await repository.documentPublicationReceipt(result.documentId);
      relationshipResult = await repository.documentRelationships(result.documentId);
    }
    if (!mounted) return;
    setState(() {
      article = result;
      provenance = provenanceResult;
      publicationReceipt = publicationReceiptResult;
      relationships = relationshipResult;
      loading = false;
    });
  }


  Future<void> _saveFavorite() async {
    final services = CodoServicesScope.of(context);
    final codoId = article?.codoId ?? widget.codoId;
    if (codoId == null || codoId.isEmpty) return;
    if (!services.auth.isSignedIn) {
      await Navigator.pushNamed(context, CodoRoutes.auth);
      return;
    }
    final repo = services.user;
    if (repo == null) return;
    setState(() {
      savingFavorite = true;
      favoriteMessage = null;
    });
    try {
      await repo.addFavorite('article', codoId);
      if (mounted) setState(() => favoriteMessage = 'Article enregistré dans vos favoris.');
    } catch (_) {
      if (mounted) setState(() => favoriteMessage = 'Impossible d’enregistrer cet article pour le moment.');
    } finally {
      if (mounted) setState(() => savingFavorite = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: CodoLogo(compact: true)),
      body: loading
          ? const Padding(padding: EdgeInsets.all(20), child: LinearProgressIndicator())
          : ListView(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
              children: [
                Text('Article de loi', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 20),
                if (article == null)
                  const SourceRequiredCard(
                    detail: 'La fiche ne doit contenir ni texte officiel ni explication tant qu’une version vérifiée n’est pas disponible.',
                  )
                else ...[
                  Text(article!.label, style: Theme.of(context).textTheme.headlineMedium),
                  const SizedBox(height: 10),
                  LegalStatusBadge(status: article!.status),
                  const SizedBox(height: 14),
                  Align(
                    alignment: Alignment.centerLeft,
                    child: OutlinedButton.icon(
                      onPressed: savingFavorite ? null : _saveFavorite,
                      icon: const Icon(Icons.bookmark_add_outlined),
                      label: Text(savingFavorite ? 'Enregistrement…' : 'Enregistrer'),
                    ),
                  ),
                  if (favoriteMessage != null) ...[
                    const SizedBox(height: 8),
                    Text(favoriteMessage!, style: Theme.of(context).textTheme.bodySmall),
                  ],
                  const SizedBox(height: 24),
                  Text('Texte officiel', style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 10),
                  SelectableText(article!.officialText, style: Theme.of(context).textTheme.bodyLarge),
                  if (article!.explanation != null) ...[
                    const SizedBox(height: 28),
                    Text('Comprendre cet article', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 10),
                    Text(article!.explanation!),
                  ],
                  const SizedBox(height: 28),
                  LegalSourceCard(source: article!.source, articleLabel: article!.label, version: article!.version),
                  if (relationships.isNotEmpty) ...[
                    const SizedBox(height: 28),
                    Text('Relations juridiques', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 8),
                    Text(
                      'Liens publies apres validation humaine du graphe juridique.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 12),
                    ...relationships.map(
                      (relationship) => ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: const Icon(Icons.account_tree_outlined),
                        title: Text(relationship.relationType),
                        subtitle: Text(
                          '${relationship.fromDocumentCodoId ?? '-'} -> ${relationship.toDocumentCodoId ?? '-'}'
                          '${relationship.evidenceSourceName == null ? '' : '\nSource: ${relationship.evidenceSourceName}'}',
                        ),
                      ),
                    ),
                  ],
                  if (publicationReceipt != null) ...[
                    const SizedBox(height: 28),
                    Text('Reçu de publication', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 8),
                    Text(
                      'Empreinte de la version juridiquement validée puis publiée par CODO.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 12),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        border: Border.all(color: Theme.of(context).dividerColor),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Version ${publicationReceipt!.versionKey}', style: const TextStyle(fontWeight: FontWeight.w700)),
                          const SizedBox(height: 8),
                          SelectableText('Publication SHA-256 ${publicationReceipt!.publicationHash}', style: Theme.of(context).textTheme.bodySmall),
                          const SizedBox(height: 4),
                          SelectableText('Source SHA-256 ${publicationReceipt!.sourceSnapshotHash}', style: Theme.of(context).textTheme.bodySmall),
                        ],
                      ),
                    ),
                  ],
                  if (provenance != null && provenance!.sources.isNotEmpty) ...[
                    const SizedBox(height: 28),
                    Text('Provenance documentaire', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 8),
                    Text(
                      'Empreintes et captures ayant servi à valider la version ${provenance!.versionKey}.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 12),
                    ...provenance!.sources.map(
                      (source) => Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            border: Border.all(color: Theme.of(context).dividerColor),
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(source.sourceName, style: const TextStyle(fontWeight: FontWeight.w700)),
                              const SizedBox(height: 4),
                              Text('${source.trustLevel.code} • ${source.provenanceRole}', style: Theme.of(context).textTheme.bodySmall),
                              const SizedBox(height: 8),
                              SelectableText('SHA-256 ${source.contentHash}', style: Theme.of(context).textTheme.bodySmall),
                              const SizedBox(height: 4),
                              SelectableText(source.sourceUrl.toString(), style: Theme.of(context).textTheme.bodySmall),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ],
                const SizedBox(height: 24),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => Navigator.pushNamed(context, CodoRoutes.articleHistory, arguments: widget.codoId),
                        child: const Text('Historique'),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => Navigator.pushNamed(context, CodoRoutes.versionCompare),
                        child: const Text('Comparer'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
    );
  }
}
