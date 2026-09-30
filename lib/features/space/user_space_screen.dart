import 'package:flutter/material.dart';

import '../../core/di/codo_services.dart';
import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_logo.dart';

class UserSpaceScreen extends StatelessWidget {
  const UserSpaceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final services = CodoServicesScope.of(context);
    const items = [
      ('Mes textes', Icons.bookmark_outline_rounded, CodoRoutes.favorites),
      ('Mes alertes', Icons.notifications_none_rounded, CodoRoutes.alerts),
      ('Mes dossiers', Icons.folder_outlined, CodoRoutes.folders),
      ('Ma veille juridique', Icons.radar_outlined, CodoRoutes.monitoring),
      ('CODO Pro', Icons.work_outline_rounded, CodoRoutes.pro),
      ('Paramètres et accessibilité', Icons.tune_rounded, CodoRoutes.accessibility),
      ('Back-office juridique', Icons.admin_panel_settings_outlined, CodoRoutes.admin),
    ];
    return Scaffold(
      appBar: AppBar(title: const CodoLogo(compact: true)),
      body: AnimatedBuilder(
        animation: services.auth,
        builder: (context, _) => ListView(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
          children: [
            Text('Mon espace', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text(
              services.auth.isSignedIn
                  ? 'Votre session CODO est active. Les données personnelles restent séparées du corpus juridique.'
                  : 'La création de compte reste facultative pour les recherches ordinaires.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 20),
            FilledButton(
              onPressed: () => Navigator.pushNamed(context, CodoRoutes.auth),
              child: Text(services.auth.isSignedIn ? 'Gérer mon compte' : 'Se connecter ou créer un compte'),
            ),
            const SizedBox(height: 24),
            ...items.map((item) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(item.$2),
                  title: Text(item.$1),
                  trailing: const Icon(Icons.chevron_right_rounded),
                  onTap: () => Navigator.pushNamed(context, item.$3),
                )),
          ],
        ),
      ),
    );
  }
}
