class AppConfig {
  const AppConfig({
    required this.apiBaseUrl,
    required this.oidcIssuer,
    required this.oidcClientId,
    required this.oidcRedirectUrl,
    required this.oidcPostLogoutRedirectUrl,
    required this.oidcScopes,
    required this.oidcAllowInsecureHttp,
  });

  final String apiBaseUrl;
  final String oidcIssuer;
  final String oidcClientId;
  final String oidcRedirectUrl;
  final String oidcPostLogoutRedirectUrl;
  final List<String> oidcScopes;
  final bool oidcAllowInsecureHttp;

  bool get hasApi => apiBaseUrl.trim().isNotEmpty;

  bool get hasOidc =>
      oidcIssuer.trim().isNotEmpty &&
      oidcClientId.trim().isNotEmpty &&
      oidcRedirectUrl.trim().isNotEmpty;

  String get oidcDiscoveryUrl =>
      '${oidcIssuer.replaceFirst(RegExp(r'/$'), '')}/.well-known/openid-configuration';

  factory AppConfig.fromEnvironment() {
    const rawScopes = String.fromEnvironment(
      'CODO_OIDC_SCOPES',
      defaultValue: 'openid,profile,email,offline_access',
    );
    return AppConfig(
      apiBaseUrl: const String.fromEnvironment('CODO_API_BASE_URL', defaultValue: ''),
      oidcIssuer: const String.fromEnvironment('CODO_OIDC_ISSUER', defaultValue: ''),
      oidcClientId: const String.fromEnvironment('CODO_OIDC_CLIENT_ID', defaultValue: ''),
      oidcRedirectUrl: const String.fromEnvironment('CODO_OIDC_REDIRECT_URL', defaultValue: ''),
      oidcPostLogoutRedirectUrl: const String.fromEnvironment(
        'CODO_OIDC_POST_LOGOUT_REDIRECT_URL',
        defaultValue: '',
      ),
      oidcScopes: rawScopes
          .split(',')
          .map((value) => value.trim())
          .where((value) => value.isNotEmpty)
          .toList(growable: false),
      oidcAllowInsecureHttp: const bool.fromEnvironment(
        'CODO_OIDC_ALLOW_INSECURE_HTTP',
        defaultValue: false,
      ),
    );
  }
}
