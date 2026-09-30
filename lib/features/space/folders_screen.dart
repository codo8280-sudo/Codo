import 'package:flutter/material.dart';

import '../../core/di/codo_services.dart';
import '../../core/navigation/codo_routes.dart';
import '../../core/network/api_client.dart';
import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';
import '../../data/repositories/http_user_repository.dart';

class FoldersScreen extends StatefulWidget {
  const FoldersScreen({super.key});

  @override
  State<FoldersScreen> createState() => _FoldersScreenState();
}

class _FoldersScreenState extends State<FoldersScreen> {
  List<UserFolder>? folders;
  String? error;
  bool loading = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (folders == null && !loading) _load();
  }

  Future<void> _load() async {
    final services = CodoServicesScope.of(context);
    if (!services.auth.isSignedIn || services.user == null) return;
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final values = await services.user!.folders();
      if (mounted) setState(() => folders = values);
    } on ApiException catch (e) {
      if (mounted) setState(() => error = e.message);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _createFolder() async {
    final name = TextEditingController();
    final description = TextEditingController();
    final accepted = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Nouveau dossier'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: name,
              autofocus: true,
              decoration: const InputDecoration(labelText: 'Nom du dossier'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: description,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Description facultative'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Annuler')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Créer')),
        ],
      ),
    );
    final folderName = name.text.trim();
    final folderDescription = description.text.trim();
    name.dispose();
    description.dispose();
    if (accepted != true || folderName.isEmpty || !mounted) return;

    try {
      final created = await CodoServicesScope.of(context).user!.createFolder(
            folderName,
            description: folderDescription.isEmpty ? null : folderDescription,
          );
      if (mounted) setState(() => folders = [created, ...?folders]);
    } on ApiException catch (e) {
      if (mounted) setState(() => error = e.message);
    }
  }

  Future<void> _deleteFolder(UserFolder folder) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Supprimer ce dossier ?'),
        content: Text('Le dossier « ${folder.name} » et son classement seront supprimés.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Annuler')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Supprimer')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    await CodoServicesScope.of(context).user!.deleteFolder(folder.id);
    if (mounted) setState(() => folders = folders?.where((item) => item.id != folder.id).toList());
  }

  @override
  Widget build(BuildContext context) {
    final services = CodoServicesScope.of(context);
    return Scaffold(
      appBar: AppBar(title: CodoLogo(compact: true)),
      floatingActionButton: services.auth.isSignedIn
          ? FloatingActionButton.extended(
              onPressed: _createFolder,
              icon: const Icon(Icons.create_new_folder_outlined),
              label: const Text('Nouveau dossier'),
            )
          : null,
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 96),
        children: [
          Text('Mes dossiers', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text(
            'Regroupez vos textes, articles, procédures et recherches sans modifier le corpus juridique.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 24),
          if (!services.auth.isSignedIn) ...[
            const CodoEmptyState(
              title: 'Connexion requise',
              message: 'Les dossiers personnels sont synchronisés uniquement lorsque vous êtes connecté.',
              icon: Icons.folder_outlined,
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
          ] else if (folders?.isEmpty ?? true) ...[
            CodoEmptyState(
              title: 'Aucun dossier',
              message: 'Créez un dossier documentaire pour classer les éléments que vous consultez.',
              actionLabel: 'Créer un dossier',
              onAction: _createFolder,
              icon: Icons.folder_outlined,
            ),
          ] else ...[
            ...folders!.map(
              (folder) => Card(
                child: ListTile(
                  leading: const Icon(Icons.folder_outlined),
                  title: Text(folder.name),
                  subtitle: Text(
                    [
                      if (folder.description?.isNotEmpty == true) folder.description!,
                      '${folder.itemCount} élément${folder.itemCount == 1 ? '' : 's'}',
                    ].join(' • '),
                  ),
                  trailing: IconButton(
                    tooltip: 'Supprimer le dossier',
                    onPressed: () => _deleteFolder(folder),
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
