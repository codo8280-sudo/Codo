import 'package:flutter/material.dart';

import 'core/config/app_config.dart';
import 'core/design/codo_theme.dart';
import 'core/di/codo_services.dart';
import 'core/navigation/codo_routes.dart';
import 'core/navigation/codo_shell.dart';

class CodoApp extends StatefulWidget {
  const CodoApp({super.key});

  @override
  State<CodoApp> createState() => _CodoAppState();
}

class _CodoAppState extends State<CodoApp> {
  late final CodoServices services;
  late final Future<void> initialization;

  @override
  void initState() {
    super.initState();
    services = CodoServices.fromConfig(AppConfig.fromEnvironment());
    initialization = services.initialize();
  }

  @override
  void dispose() {
    services.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return CodoServicesScope(
      services: services,
      child: MaterialApp(
        title: 'CODO',
        debugShowCheckedModeBanner: false,
        theme: CodoTheme.light(),
        onGenerateRoute: CodoRoutes.onGenerateRoute,
        home: FutureBuilder<void>(
          future: initialization,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Scaffold(
                body: SafeArea(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SizedBox(height: 40),
                        SizedBox(width: 110, child: LinearProgressIndicator()),
                        SizedBox(height: 28),
                        DecoratedBox(
                          decoration: BoxDecoration(color: Color(0xFFF0F1ED)),
                          child: SizedBox(height: 28, width: 260),
                        ),
                        SizedBox(height: 14),
                        DecoratedBox(
                          decoration: BoxDecoration(color: Color(0xFFF0F1ED)),
                          child: SizedBox(height: 18, width: 320),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }
            return const CodoShell();
          },
        ),
      ),
    );
  }
}
