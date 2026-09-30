import 'package:flutter/foundation.dart';
import 'package:flutter_appauth/flutter_appauth.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../config/app_config.dart';

class CodoAuthException implements Exception {
  const CodoAuthException(this.message);
  final String message;
  @override
  String toString() => message;
}

class CodoAuthCancelled implements Exception {
  const CodoAuthCancelled();
}

class CodoAuthSession {
  const CodoAuthSession({
    required this.accessToken,
    this.refreshToken,
    this.idToken,
    this.accessTokenExpiration,
  });

  final String accessToken;
  final String? refreshToken;
  final String? idToken;
  final DateTime? accessTokenExpiration;

  bool get isNearExpiry {
    final expiry = accessTokenExpiration;
    if (expiry == null) return false;
    return !expiry.isAfter(DateTime.now().toUtc().add(const Duration(seconds: 60)));
  }
}

class CodoAuthService extends ChangeNotifier {
  CodoAuthService(
    this.config, {
    FlutterAppAuth appAuth = const FlutterAppAuth(),
    FlutterSecureStorage storage = const FlutterSecureStorage(),
  })  : _appAuth = appAuth,
        _storage = storage;

  static const _accessTokenKey = 'codo_oidc_access_token';
  static const _refreshTokenKey = 'codo_oidc_refresh_token';
  static const _idTokenKey = 'codo_oidc_id_token';
  static const _expirationKey = 'codo_oidc_access_expiration';

  final AppConfig config;
  final FlutterAppAuth _appAuth;
  final FlutterSecureStorage _storage;

  CodoAuthSession? _session;
  bool _initialized = false;
  bool _busy = false;

  bool get configured => config.hasOidc;
  bool get initialized => _initialized;
  bool get busy => _busy;
  bool get isSignedIn => _session != null;

  Future<void> initialize() async {
    if (_initialized) return;
    final accessToken = await _storage.read(key: _accessTokenKey);
    if (accessToken != null && accessToken.isNotEmpty) {
      final refreshToken = await _storage.read(key: _refreshTokenKey);
      final idToken = await _storage.read(key: _idTokenKey);
      final rawExpiration = await _storage.read(key: _expirationKey);
      _session = CodoAuthSession(
        accessToken: accessToken,
        refreshToken: refreshToken,
        idToken: idToken,
        accessTokenExpiration: rawExpiration == null ? null : DateTime.tryParse(rawExpiration)?.toUtc(),
      );
    }
    _initialized = true;
    notifyListeners();

    if (_session?.isNearExpiry == true && _session?.refreshToken != null && configured) {
      try {
        await _refresh();
      } catch (_) {
        // Preserve the local session metadata. The API will reject an expired token
        // and the UI can ask the user to authenticate again instead of silently
        // treating a temporary identity-provider outage as account deletion.
      }
    }
  }

  Future<void> signIn() async {
    if (!configured) {
      throw const CodoAuthException('Le fournisseur d’identité CODO n’est pas configuré.');
    }
    _setBusy(true);
    try {
      final response = await _appAuth.authorizeAndExchangeCode(
        AuthorizationTokenRequest(
          config.oidcClientId,
          config.oidcRedirectUrl,
          discoveryUrl: config.oidcDiscoveryUrl,
          scopes: config.oidcScopes,
          allowInsecureConnections: config.oidcAllowInsecureHttp,
        ),
      );
      final accessToken = response.accessToken;
      if (accessToken == null || accessToken.isEmpty) {
        throw const CodoAuthException('Le fournisseur d’identité n’a pas retourné de jeton d’accès.');
      }
      await _save(
        CodoAuthSession(
          accessToken: accessToken,
          refreshToken: response.refreshToken,
          idToken: response.idToken,
          accessTokenExpiration: response.accessTokenExpirationDateTime?.toUtc(),
        ),
      );
    } on FlutterAppAuthUserCancelledException {
      throw const CodoAuthCancelled();
    } on FlutterAppAuthPlatformException catch (error) {
      throw CodoAuthException(error.message ?? 'Échec de l’authentification OIDC.');
    } finally {
      _setBusy(false);
    }
  }

  Future<String?> validAccessToken() async {
    if (!_initialized) await initialize();
    final session = _session;
    if (session == null) return null;
    if (!session.isNearExpiry) return session.accessToken;
    if (session.refreshToken == null || session.refreshToken!.isEmpty || !configured) {
      return session.accessToken;
    }
    await _refresh();
    return _session?.accessToken;
  }

  Future<void> _refresh() async {
    final refreshToken = _session?.refreshToken;
    if (refreshToken == null || refreshToken.isEmpty) return;
    try {
      final response = await _appAuth.token(
        TokenRequest(
          config.oidcClientId,
          config.oidcRedirectUrl,
          discoveryUrl: config.oidcDiscoveryUrl,
          refreshToken: refreshToken,
          scopes: config.oidcScopes,
          allowInsecureConnections: config.oidcAllowInsecureHttp,
        ),
      );
      final accessToken = response.accessToken;
      if (accessToken == null || accessToken.isEmpty) {
        throw const CodoAuthException('Impossible de renouveler la session CODO.');
      }
      await _save(
        CodoAuthSession(
          accessToken: accessToken,
          refreshToken: response.refreshToken ?? refreshToken,
          idToken: response.idToken ?? _session?.idToken,
          accessTokenExpiration: response.accessTokenExpirationDateTime?.toUtc(),
        ),
      );
    } on FlutterAppAuthPlatformException catch (error) {
      throw CodoAuthException(error.message ?? 'Impossible de renouveler la session CODO.');
    }
  }

  Future<void> signOut() async {
    final idToken = _session?.idToken;
    try {
      if (configured && idToken != null && idToken.isNotEmpty) {
        await _appAuth.endSession(
          EndSessionRequest(
            idTokenHint: idToken,
            postLogoutRedirectUrl: config.oidcPostLogoutRedirectUrl.trim().isEmpty
                ? null
                : config.oidcPostLogoutRedirectUrl,
            discoveryUrl: config.oidcDiscoveryUrl,
            allowInsecureConnections: config.oidcAllowInsecureHttp,
          ),
        );
      }
    } catch (_) {
      // Local sign-out must remain possible even if the identity provider is down.
    } finally {
      await clearLocalSession();
    }
  }

  Future<void> clearLocalSession() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
    await _storage.delete(key: _idTokenKey);
    await _storage.delete(key: _expirationKey);
    _session = null;
    notifyListeners();
  }

  Future<void> _save(CodoAuthSession session) async {
    await _storage.write(key: _accessTokenKey, value: session.accessToken);
    if (session.refreshToken == null) {
      await _storage.delete(key: _refreshTokenKey);
    } else {
      await _storage.write(key: _refreshTokenKey, value: session.refreshToken);
    }
    if (session.idToken == null) {
      await _storage.delete(key: _idTokenKey);
    } else {
      await _storage.write(key: _idTokenKey, value: session.idToken);
    }
    if (session.accessTokenExpiration == null) {
      await _storage.delete(key: _expirationKey);
    } else {
      await _storage.write(key: _expirationKey, value: session.accessTokenExpiration!.toIso8601String());
    }
    _session = session;
    notifyListeners();
  }

  void _setBusy(bool value) {
    if (_busy == value) return;
    _busy = value;
    notifyListeners();
  }
}
