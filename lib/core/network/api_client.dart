import 'dart:convert';
import 'dart:io';

typedef AccessTokenProvider = Future<String?> Function();

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient(
    this.baseUrl, {
    HttpClient? httpClient,
    AccessTokenProvider? accessTokenProvider,
  })  : _httpClient = httpClient ?? HttpClient(),
        _accessTokenProvider = accessTokenProvider;

  final String baseUrl;
  final HttpClient _httpClient;
  final AccessTokenProvider? _accessTokenProvider;

  Uri _uri(String path, [Map<String, String>? query]) {
    final root = Uri.parse(baseUrl.endsWith('/') ? baseUrl : '$baseUrl/');
    return root.resolve(path.replaceFirst(RegExp(r'^/'), '')).replace(queryParameters: query);
  }

  Future<void> _headers(HttpClientRequest request, {bool jsonBody = false}) async {
    request.headers.set(HttpHeaders.acceptHeader, 'application/json');
    if (jsonBody) request.headers.contentType = ContentType.json;
    final token = await _accessTokenProvider?.call();
    if (token != null && token.trim().isNotEmpty) {
      request.headers.set(HttpHeaders.authorizationHeader, 'Bearer ${token.trim()}');
    }
  }

  Future<Map<String, dynamic>> getJson(String path, {Map<String, String>? query}) async {
    final request = await _httpClient.getUrl(_uri(path, query));
    await _headers(request);
    final decoded = await _decode(await request.close());
    if (decoded is Map<String, dynamic>) return decoded;
    throw const ApiException('Réponse API CODO inattendue.');
  }

  Future<List<dynamic>> getJsonList(String path, {Map<String, String>? query}) async {
    final request = await _httpClient.getUrl(_uri(path, query));
    await _headers(request);
    final decoded = await _decode(await request.close());
    if (decoded is List<dynamic>) return decoded;
    throw const ApiException('Réponse API CODO inattendue.');
  }

  Future<Map<String, dynamic>> postJson(String path, Map<String, dynamic> body) async {
    final request = await _httpClient.postUrl(_uri(path));
    await _headers(request, jsonBody: true);
    request.write(jsonEncode(body));
    final decoded = await _decode(await request.close());
    if (decoded is Map<String, dynamic>) return decoded;
    throw const ApiException('Réponse API CODO inattendue.');
  }

  Future<Map<String, dynamic>> putJson(String path, Map<String, dynamic> body) async {
    final request = await _httpClient.putUrl(_uri(path));
    await _headers(request, jsonBody: true);
    request.write(jsonEncode(body));
    final decoded = await _decode(await request.close());
    if (decoded is Map<String, dynamic>) return decoded;
    throw const ApiException('Réponse API CODO inattendue.');
  }

  Future<Map<String, dynamic>> patchJson(String path, Map<String, dynamic> body) async {
    final request = await _httpClient.patchUrl(_uri(path));
    await _headers(request, jsonBody: true);
    request.write(jsonEncode(body));
    final decoded = await _decode(await request.close());
    if (decoded is Map<String, dynamic>) return decoded;
    throw const ApiException('Réponse API CODO inattendue.');
  }

  Future<void> delete(String path) async {
    final request = await _httpClient.deleteUrl(_uri(path));
    await _headers(request);
    await _decode(await request.close());
  }

  Future<dynamic> _decode(HttpClientResponse response) async {
    final raw = await utf8.decoder.bind(response).join();
    dynamic payload;
    if (raw.trim().isNotEmpty) {
      payload = jsonDecode(raw);
    }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      String? detail;
      String? message;
      if (payload is Map) {
        detail = payload['detail'] is String ? payload['detail'] as String : null;
        message = payload['message'] is String ? payload['message'] as String : null;
      }
      throw ApiException(
        detail ?? message ?? 'Erreur API CODO',
        statusCode: response.statusCode,
      );
    }
    return payload;
  }

  void close() => _httpClient.close(force: true);
}
