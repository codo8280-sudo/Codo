import 'package:flutter/widgets.dart';

import '../../data/repositories/http_legal_repositories.dart';
import '../../data/repositories/http_user_repository.dart';
import '../../data/repositories/unconfigured_repositories.dart';
import '../../domain/repositories/legal_repositories.dart';
import '../auth/codo_auth_service.dart';
import '../config/app_config.dart';
import '../network/api_client.dart';

class CodoServices {
  CodoServices({
    required this.auth,
    required this.legalCorpus,
    required this.ai,
    required this.user,
    this.apiClient,
  });

  final CodoAuthService auth;
  final LegalCorpusRepository legalCorpus;
  final CodoAiRepository ai;
  final HttpUserRepository? user;
  final ApiClient? apiClient;

  factory CodoServices.fromConfig(AppConfig config) {
    final auth = CodoAuthService(config);
    if (!config.hasApi) {
      return CodoServices(
        auth: auth,
        legalCorpus: const UnconfiguredLegalCorpusRepository(),
        ai: const UnconfiguredCodoAiRepository(),
        user: null,
      );
    }
    final client = ApiClient(
      config.apiBaseUrl,
      accessTokenProvider: auth.validAccessToken,
    );
    return CodoServices(
      auth: auth,
      legalCorpus: HttpLegalCorpusRepository(client),
      ai: HttpCodoAiRepository(client),
      user: HttpUserRepository(client),
      apiClient: client,
    );
  }

  Future<void> initialize() => auth.initialize();

  void dispose() {
    auth.dispose();
    apiClient?.close();
  }
}

class CodoServicesScope extends InheritedWidget {
  const CodoServicesScope({super.key, required this.services, required super.child});

  final CodoServices services;

  static CodoServices of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<CodoServicesScope>();
    assert(scope != null, 'CodoServicesScope absent de l arbre de widgets');
    return scope!.services;
  }

  @override
  bool updateShouldNotify(CodoServicesScope oldWidget) => oldWidget.services != services;
}
