import 'package:flutter/material.dart';

import '../../core/di/codo_services.dart';
import '../../core/navigation/codo_routes.dart';
import '../../core/network/api_client.dart';
import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';
import '../../data/repositories/http_user_repository.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> {
  List<UserAlert>? alerts;
  bool loading = false;
  String? error;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (alerts == null && !loading) _load();
  }

  Future<void> _load() async {
    final services = CodoServicesScope.of(context);
    if (!services.auth.isSignedIn || services.user == null) return;
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final values = await services.user!.alerts();
      if (mounted) setState(() => alerts = values);
    } on ApiException catch (e) {
      if (mounted) setState(() => error = e.message);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _createAlert() async {
    final key = TextEditingController();
    var scope = 'document';
    final result = await showDialog<(String, String)?>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Ajouter une veille'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                initialValue: scope,
                decoration: const InputDecoration(labelText: 'Portée'),
                items: const [
                  DropdownMenuItem(value: 'document', child: Text('Texte juridique')),
                  DropdownMenuItem(value: 'article', child: Text('Article')),
                  DropdownMenuItem(value: 'domain', child: Text('Domaine juridique')),
                  DropdownMenuItem(value: 'topic', child: Text('Thématique')),
                ],
                onChanged: (value) => setDialogState(() => scope = value ?? scope),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: key,
                autofocus: true,
                decoration: const InputDecoration(
                  labelText: 'Référence ou identifiant',
                  helperText: 'Ex. CODO-CI-CONST-2016 ou droit-travail',
                ),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Annuler')),
            FilledButton(
              onPressed: () {
                final value = key.text.trim();
                if (value.isNotEmpty) Navigator.pop(context, (scope, value));
              },
              child: const Text('Ajouter'),
            ),
          ],
        ),
      ),
    );
    key.dispose();
    if (result == null || !mounted) return;
    try {
      final created = await CodoServicesScope.of(context).user!.createAlert(result.$1, result.$2);
      if (mounted) {
        setState(() {
          final existing = alerts?.where((item) => item.id != created.id).toList() ?? <UserAlert>[];
          alerts = [created, ...existing];
        });
      }
    } on ApiException catch (e) {
      if (mounted) setState(() => error = e.message);
    }
  }

  Future<void> _toggle(UserAlert alert, bool value) async {
    final updated = await CodoServicesScope.of(context).user!.updateAlert(alert.id, value);
    if (!mounted) return;
    setState(() => alerts = alerts?.map((item) => item.id == updated.id ? updated : item).toList());
  }

  Future<void> _delete(UserAlert alert) async {
    await CodoServicesScope.of(context).user!.deleteAlert(alert.id);
    if (mounted) setState(() => alerts = alerts?.where((item) => item.id != alert.id).toList());
  }

  String _scopeLabel(String scope) => switch (scope) {
        'document' => 'Texte',
        'article' => 'Article',
        'domain' => 'Domaine',
        'topic' => 'Thématique',
        _ => scope,
      };

  @override
  Widget build(BuildContext context) {
    final services = CodoServicesScope.of(context);
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      floatingActionButton: services.auth.isSignedIn
          ? FloatingActionButton.extended(
              onPressed: _createAlert,
              icon: const Icon(Icons.add_alert_outlined),
              label: const Text('Ajouter une veille'),
            )
          : null,
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 96),
        children: [
          Text('Mes alertes', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text(
            'Une alerte n’est déclenchée qu’à partir d’une évolution juridiquement vérifiée par CODO.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 24),
          if (!services.auth.isSignedIn) ...[
            const CodoEmptyState(
              title: 'Connexion requise',
              message: 'La veille personnalisée nécessite un compte. La recherche juridique reste publique.',
              icon: Icons.notifications_none_rounded,
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () => Navigator.pushNamed(context, CodoRoutes.auth),
              child: const Text('Se connecter'),
            ),
          ] else if (loading) ...[
            const LinearProgressIndicator(),
          ] else if (error != null) ...[
            Text(error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
            const SizedBox(height: 12),
            OutlinedButton(onPressed: _load, child: const Text('Réessayer')),
          ] else if (alerts?.isEmpty ?? true) ...[
            CodoEmptyState(
              title: 'Aucune alerte configurée',
              message: 'Ajoutez un texte, un article, un domaine ou une thématique à votre veille.',
              actionLabel: 'Ajouter une veille',
              onAction: _createAlert,
              icon: Icons.notifications_none_rounded,
            ),
          ] else ...[
            ...alerts!.map(
              (alert) => Card(
                child: SwitchListTile(
                  value: alert.enabled,
                  onChanged: (value) => _toggle(alert, value),
                  title: Text(alert.scopeKey),
                  subtitle: Text(_scopeLabel(alert.scopeType)),
                  secondary: IconButton(
                    tooltip: 'Supprimer cette veille',
                    onPressed: () => _delete(alert),
                    icon: const Icon(Icons.delete_outline_rounded),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
