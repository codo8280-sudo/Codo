import 'package:flutter/material.dart';

import '../../core/di/codo_services.dart';
import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/legal_status_badge.dart';
import '../../domain/models/legal_models.dart';

class ArticleHistoryScreen extends StatefulWidget {
  const ArticleHistoryScreen({super.key, this.codoId});

  final String? codoId;

  @override
  State<ArticleHistoryScreen> createState() => _ArticleHistoryScreenState();
}

class _ArticleHistoryScreenState extends State<ArticleHistoryScreen> {
  List<LegalArticleVersion> versions = const [];
  bool loading = false;

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
    final data = await CodoServicesScope.of(context).legalCorpus.articleHistory(widget.codoId!);
    if (!mounted) return;
    setState(() {
      versions = data;
      loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const CodoLogo(compact: true)),
      body: loading
          ? const Padding(padding: EdgeInsets.all(20), child: LinearProgressIndicator())
          : ListView(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
              children: [
                Text('Historique de l’article', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 8),
                Text('Aucune ancienne disposition ne doit être détruite après une modification.', style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 24),
                if (versions.isEmpty)
                  const CodoEmptyState(
                    title: 'Historique non chargé',
                    message: 'Les versions apparaîtront ici après validation du versionnement temporel du corpus.',
                    icon: Icons.history_rounded,
                  )
                else
                  ...versions.map((v) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Card(
                          child: Padding(
                            padding: const EdgeInsets.all(18),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Expanded(child: Text(v.versionKey, style: const TextStyle(fontWeight: FontWeight.w700))),
                                    LegalStatusBadge(status: v.status),
                                  ],
                                ),
                                const SizedBox(height: 10),
                                Text(v.officialText, maxLines: 4, overflow: TextOverflow.ellipsis),
                              ],
                            ),
                          ),
                        ),
                      )),
              ],
            ),
    );
  }
}
