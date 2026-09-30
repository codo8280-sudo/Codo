import 'package:flutter/material.dart';

import '../../core/di/codo_services.dart';
import '../../core/navigation/codo_routes.dart';
import '../../core/network/api_client.dart';
import '../../core/widgets/codo_empty_state.dart';
import '../../core/widgets/codo_logo.dart';
import '../../data/repositories/http_user_repository.dart';

class FavoritesScreen extends StatefulWidget {
  const FavoritesScreen({super.key});

  @override
  State<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  List<UserFavorite>? favorites;
  String? error;
  bool loading = false;

  Future<void> _load() async {
    final services = CodoServicesScope.of(context);
    if (!services.auth.isSignedIn || services.user == null) return;
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final values = await services.user!.favorites();
      if (mounted) setState(() => favorites = values);
    } on ApiException catch (e) {
      if (mounted) setState(() => error = e.message);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (favorites == null && !loading) _load();
  }

  Future<void> _remove(UserFavorite favorite) async {
    final repo = CodoServicesScope.of(context).user;
    if (repo == null) return;
    await repo.removeFavorite(favorite.id);
    if (mounted) setState(() => favorites = favorites?.where((item) => item.id != favorite.id).toList());
  }

  @override
  Widget build(BuildContext context) {
    final services = CodoServicesScope.of(context);
    return Scaffold(
      appBar: AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('Mes favoris', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 24),
          if (!services.auth.isSignedIn) ...[
            const CodoEmptyState(
              title: 'Connexion requise pour les favoris synchronisés',
              message: 'La consultation du droit reste disponible sans compte.',
              icon: Icons.bookmark_outline_rounded,
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
          ] else if (favorites?.isEmpty ?? true) ...[
            const CodoEmptyState(
              title: 'Aucun texte enregistré',
              message: 'Enregistrez un article ou une loi pour les retrouver rapidement ici.',
              icon: Icons.bookmark_outline_rounded,
            ),
          ] else ...[
            ...favorites!.map(
              (favorite) => ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Icon(favorite.entityType == 'article' ? Icons.article_outlined : Icons.description_outlined),
                title: Text(favorite.entityKey),
                subtitle: Text(favorite.entityType),
                trailing: IconButton(
                  tooltip: 'Retirer des favoris',
                  onPressed: () => _remove(favorite),
                  icon: const Icon(Icons.bookmark_remove_outlined),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
