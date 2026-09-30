import 'package:flutter/material.dart';

import '../../core/auth/codo_auth_service.dart';
import '../../core/di/codo_services.dart';
import '../../core/network/api_client.dart';
import '../../core/widgets/codo_logo.dart';
import '../../data/repositories/http_user_repository.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  UserProfile? profile;
  String? error;
  bool loadingProfile = false;
  CodoAuthService? _auth;

  CodoServices get services => CodoServicesScope.of(context);

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final next = services.auth;
    if (!identical(_auth, next)) {
      _auth?.removeListener(_authChanged);
      _auth = next;
      _auth!.addListener(_authChanged);
    }
    _loadProfileIfNeeded();
  }

  @override
  void dispose() {
    _auth?.removeListener(_authChanged);
    super.dispose();
  }

  void _authChanged() {
    if (!mounted) return;
    setState(() {});
    _loadProfileIfNeeded();
  }

  Future<void> _loadProfileIfNeeded() async {
    if (!services.auth.isSignedIn || services.user == null || loadingProfile) return;
    setState(() => loadingProfile = true);
    try {
      final value = await services.user!.profile();
      if (mounted) setState(() => profile = value);
    } on ApiException catch (e) {
      if (mounted) setState(() => error = e.message);
    } finally {
      if (mounted) setState(() => loadingProfile = false);
    }
  }

  Future<void> _signIn() async {
    setState(() => error = null);
    try {
      await services.auth.signIn();
      await _loadProfileIfNeeded();
    } on CodoAuthCancelled {
      return;
    } on CodoAuthException catch (e) {
      if (mounted) setState(() => error = e.message);
    } catch (_) {
      if (mounted) setState(() => error = 'La connexion n’a pas pu être finalisée.');
    }
  }

  Future<void> _signOut() async {
    setState(() => error = null);
    await services.auth.signOut();
    if (mounted) setState(() => profile = null);
  }

  Future<void> _deleteAccount() async {
    final repo = services.user;
    if (repo == null) return;
    final approved = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Supprimer mon compte ?'),
        content: const Text(
          'Cette action supprime votre profil CODO ainsi que vos favoris, dossiers, alertes et réglages liés au compte.',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Annuler')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Supprimer')),
        ],
      ),
    );
    if (approved != true) return;
    try {
      await repo.deleteAccount();
      await services.auth.signOut();
      if (mounted) setState(() => profile = null);
    } on ApiException catch (e) {
      if (mounted) setState(() => error = e.message);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = services.auth;
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Connexion', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text(
            'Le compte reste facultatif pour consulter et rechercher le droit. Il sert aux favoris, alertes, dossiers et réglages synchronisés.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 28),
          if (!auth.configured) ...[
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text('OIDC n’est pas encore configuré pour cette installation CODO.'),
              ),
            ),
          ] else if (!auth.isSignedIn) ...[
            FilledButton.icon(
              onPressed: auth.busy ? null : _signIn,
              icon: const Icon(Icons.login_rounded),
              label: Text(auth.busy ? 'Connexion…' : 'Se connecter / créer un compte'),
            ),
            const SizedBox(height: 12),
            Text(
              'L’authentification utilise le navigateur système et PKCE. CODO ne collecte pas votre mot de passe.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ] else ...[
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const CircleAvatar(child: Icon(Icons.person_outline_rounded)),
              title: Text(profile?.displayName ?? 'Compte CODO'),
              subtitle: Text(profile?.email ?? 'Session OIDC active'),
            ),
            if (profile?.emailVerified == true)
              const Text('Adresse e-mail vérifiée par le fournisseur d’identité.'),
            const SizedBox(height: 16),
            OutlinedButton(onPressed: auth.busy ? null : _signOut, child: const Text('Se déconnecter')),
            const SizedBox(height: 12),
            TextButton(
              onPressed: _deleteAccount,
              child: const Text('Supprimer mon compte CODO'),
            ),
          ],
          if (loadingProfile) ...[
            const SizedBox(height: 18),
            const LinearProgressIndicator(),
          ],
          if (error != null) ...[
            const SizedBox(height: 18),
            Text(error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ],
        ],
      ),
    );
  }
}
