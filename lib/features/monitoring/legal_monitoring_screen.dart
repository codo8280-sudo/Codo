import 'package:flutter/material.dart';

import '../../core/di/codo_services.dart';
import '../../core/navigation/codo_routes.dart';
import '../../core/widgets/codo_logo.dart';

class LegalMonitoringScreen extends StatelessWidget {
  const LegalMonitoringScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final services = CodoServicesScope.of(context);
    return Scaffold(
      appBar: AppBar(title: const CodoLogo(compact: true)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          Text('Ma veille juridique', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text(
            'Suivez les matières et textes qui comptent pour vous. CODO distingue toujours une évolution détectée d’une modification juridiquement vérifiée.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 24),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.radar_outlined, size: 32),
                  const SizedBox(height: 16),
                  Text(
                    services.auth.isSignedIn ? 'Gérer mes abonnements' : 'Connexion nécessaire pour une veille personnalisée',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  const Text('Les anciennes versions restent consultables et les relations de modification doivent être validées avant exposition publique.'),
                  const SizedBox(height: 18),
                  FilledButton(
                    onPressed: () => Navigator.pushNamed(
                      context,
                      services.auth.isSignedIn ? CodoRoutes.alerts : CodoRoutes.auth,
                    ),
                    child: Text(services.auth.isSignedIn ? 'Ouvrir mes alertes' : 'Se connecter'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
