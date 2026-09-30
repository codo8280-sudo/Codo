import 'package:flutter/material.dart';

import '../../core/di/codo_services.dart';
import '../../core/network/api_client.dart';
import '../../core/widgets/codo_logo.dart';
import '../../data/repositories/http_user_repository.dart';

class AccessibilityScreen extends StatefulWidget {
  const AccessibilityScreen({super.key});

  @override
  State<AccessibilityScreen> createState() => _AccessibilityScreenState();
}

class _AccessibilityScreenState extends State<AccessibilityScreen> {
  double textScale = 1.0;
  bool highContrast = false;
  bool reducedMotion = false;
  bool offlineCache = false;
  bool loadedRemote = false;
  bool saving = false;
  String? message;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _loadRemoteOnce();
  }

  Future<void> _loadRemoteOnce() async {
    if (loadedRemote) return;
    final services = CodoServicesScope.of(context);
    if (!services.auth.isSignedIn || services.user == null) return;
    loadedRemote = true;
    try {
      final settings = await services.user!.accessibility();
      if (!mounted) return;
      setState(() {
        textScale = settings.textScale;
        highContrast = settings.highContrast;
        reducedMotion = settings.reduceMotion;
        offlineCache = settings.offlineCacheEnabled;
      });
    } on ApiException catch (e) {
      if (mounted) setState(() => message = e.message);
    }
  }

  Future<void> _save() async {
    final services = CodoServicesScope.of(context);
    final repo = services.user;
    if (!services.auth.isSignedIn || repo == null) {
      setState(() => message = 'Connectez-vous pour synchroniser ces réglages entre vos appareils.');
      return;
    }
    setState(() {
      saving = true;
      message = null;
    });
    try {
      await repo.updateAccessibility(UserAccessibilitySettings(
        textScale: textScale,
        highContrast: highContrast,
        reduceMotion: reducedMotion,
        offlineCacheEnabled: offlineCache,
      ));
      if (mounted) setState(() => message = 'Réglages synchronisés.');
    } on ApiException catch (e) {
      if (mounted) setState(() => message = e.message);
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const AppBar(title: CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Paramètres et accessibilité', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 24),
          Text('Taille du texte : ${textScale.toStringAsFixed(1)}×'),
          Slider(value: textScale, min: 0.8, max: 1.8, divisions: 10, onChanged: (v) => setState(() => textScale = v)),
          SwitchListTile(contentPadding: EdgeInsets.zero, title: const Text('Contraste renforcé'), value: highContrast, onChanged: (v) => setState(() => highContrast = v)),
          SwitchListTile(contentPadding: EdgeInsets.zero, title: const Text('Réduire les animations'), value: reducedMotion, onChanged: (v) => setState(() => reducedMotion = v)),
          SwitchListTile(contentPadding: EdgeInsets.zero, title: const Text('Mettre en cache les textes importants'), subtitle: const Text('Préparation du mode faible connexion / hors connexion.'), value: offlineCache, onChanged: (v) => setState(() => offlineCache = v)),
          const SizedBox(height: 16),
          FilledButton(onPressed: saving ? null : _save, child: Text(saving ? 'Synchronisation…' : 'Enregistrer les réglages')),
          if (message != null) ...[
            const SizedBox(height: 12),
            Text(message!, style: Theme.of(context).textTheme.bodySmall),
          ],
          const SizedBox(height: 18),
          const ListTile(contentPadding: EdgeInsets.zero, leading: Icon(Icons.record_voice_over_outlined), title: Text('Lecture audio'), subtitle: Text('Prévue dans la feuille de route mobile.')),
          const ListTile(contentPadding: EdgeInsets.zero, leading: Icon(Icons.mic_none_rounded), title: Text('Commande vocale'), subtitle: Text('Prévue après connexion du service vocal.')),
        ],
      ),
    );
  }
}
