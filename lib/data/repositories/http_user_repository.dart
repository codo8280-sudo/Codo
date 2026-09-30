import '../../core/network/api_client.dart';

class UserProfile {
  const UserProfile({
    required this.id,
    required this.subject,
    required this.issuer,
    required this.locale,
    required this.emailVerified,
    this.displayName,
    this.email,
  });

  final String id;
  final String subject;
  final String issuer;
  final String? displayName;
  final String? email;
  final bool emailVerified;
  final String locale;

  factory UserProfile.fromJson(Map<String, dynamic> json) => UserProfile(
        id: json['id'] as String? ?? '',
        subject: json['auth_subject'] as String? ?? '',
        issuer: json['auth_issuer'] as String? ?? '',
        displayName: json['display_name'] as String?,
        email: json['email'] as String?,
        emailVerified: json['email_verified'] == true,
        locale: json['locale'] as String? ?? 'fr-CI',
      );
}

class UserAccessibilitySettings {
  const UserAccessibilitySettings({
    required this.textScale,
    required this.highContrast,
    required this.reduceMotion,
    required this.offlineCacheEnabled,
  });

  final double textScale;
  final bool highContrast;
  final bool reduceMotion;
  final bool offlineCacheEnabled;

  factory UserAccessibilitySettings.fromJson(Map<String, dynamic> json) => UserAccessibilitySettings(
        textScale: (json['text_scale'] as num?)?.toDouble() ?? 1.0,
        highContrast: json['high_contrast'] == true,
        reduceMotion: json['reduce_motion'] == true,
        offlineCacheEnabled: json['offline_cache_enabled'] == true,
      );

  Map<String, dynamic> toJson() => {
        'text_scale': textScale,
        'high_contrast': highContrast,
        'reduce_motion': reduceMotion,
        'offline_cache_enabled': offlineCacheEnabled,
      };
}

class UserFavorite {
  const UserFavorite({
    required this.id,
    required this.entityType,
    required this.entityKey,
  });

  final int id;
  final String entityType;
  final String entityKey;

  factory UserFavorite.fromJson(Map<String, dynamic> json) => UserFavorite(
        id: json['id'] as int? ?? 0,
        entityType: json['entity_type'] as String? ?? '',
        entityKey: json['entity_key'] as String? ?? '',
      );
}


class UserFolder {
  const UserFolder({
    required this.id,
    required this.name,
    required this.itemCount,
    this.description,
  });

  final String id;
  final String name;
  final String? description;
  final int itemCount;

  factory UserFolder.fromJson(Map<String, dynamic> json) => UserFolder(
        id: json['id'] as String? ?? '',
        name: json['name'] as String? ?? '',
        description: json['description'] as String?,
        itemCount: json['item_count'] as int? ?? 0,
      );
}

class UserAlert {
  const UserAlert({
    required this.id,
    required this.scopeType,
    required this.scopeKey,
    required this.enabled,
  });

  final String id;
  final String scopeType;
  final String scopeKey;
  final bool enabled;

  factory UserAlert.fromJson(Map<String, dynamic> json) => UserAlert(
        id: json['id'] as String? ?? '',
        scopeType: json['scope_type'] as String? ?? '',
        scopeKey: json['scope_key'] as String? ?? '',
        enabled: json['enabled'] == true,
      );
}

class HttpUserRepository {
  const HttpUserRepository(this._client);
  final ApiClient _client;

  Future<UserProfile> profile() async => UserProfile.fromJson(await _client.getJson('/v1/me'));

  Future<UserProfile> updateProfile({String? displayName, String? locale}) async =>
      UserProfile.fromJson(await _client.patchJson('/v1/me', {
        if (displayName != null) 'display_name': displayName,
        if (locale != null) 'locale': locale,
      }));

  Future<void> deleteAccount() => _client.delete('/v1/me');

  Future<UserAccessibilitySettings> accessibility() async =>
      UserAccessibilitySettings.fromJson(await _client.getJson('/v1/me/accessibility'));

  Future<UserAccessibilitySettings> updateAccessibility(UserAccessibilitySettings settings) async =>
      UserAccessibilitySettings.fromJson(await _client.putJson('/v1/me/accessibility', settings.toJson()));

  Future<List<UserFavorite>> favorites() async =>
      (await _client.getJsonList('/v1/me/favorites'))
          .whereType<Map>()
          .map((item) => UserFavorite.fromJson(item.cast<String, dynamic>()))
          .toList(growable: false);

  Future<UserFavorite> addFavorite(String entityType, String entityKey) async =>
      UserFavorite.fromJson(await _client.postJson('/v1/me/favorites', {
        'entity_type': entityType,
        'entity_key': entityKey,
      }));

  Future<void> removeFavorite(int id) => _client.delete('/v1/me/favorites/$id');

  Future<List<UserFolder>> folders() async =>
      (await _client.getJsonList('/v1/me/folders'))
          .whereType<Map>()
          .map((item) => UserFolder.fromJson(item.cast<String, dynamic>()))
          .toList(growable: false);

  Future<UserFolder> createFolder(String name, {String? description}) async =>
      UserFolder.fromJson(await _client.postJson('/v1/me/folders', {
        'name': name,
        if (description != null && description.trim().isNotEmpty) 'description': description.trim(),
      }));

  Future<void> deleteFolder(String id) => _client.delete('/v1/me/folders/$id');

  Future<List<UserAlert>> alerts() async =>
      (await _client.getJsonList('/v1/me/alerts'))
          .whereType<Map>()
          .map((item) => UserAlert.fromJson(item.cast<String, dynamic>()))
          .toList(growable: false);

  Future<UserAlert> createAlert(String scopeType, String scopeKey) async =>
      UserAlert.fromJson(await _client.postJson('/v1/me/alerts', {
        'scope_type': scopeType,
        'scope_key': scopeKey,
      }));

  Future<UserAlert> updateAlert(String id, bool enabled) async =>
      UserAlert.fromJson(await _client.patchJson('/v1/me/alerts/$id', {'enabled': enabled}));

  Future<void> deleteAlert(String id) => _client.delete('/v1/me/alerts/$id');

}
