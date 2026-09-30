import '../../core/network/api_client.dart';
import '../../domain/models/legal_models.dart';
import '../../domain/repositories/legal_repositories.dart';

class HttpLegalCorpusRepository implements LegalCorpusRepository {
  HttpLegalCorpusRepository(this._client);

  final ApiClient _client;

  @override
  Future<List<LegalSearchResult>> search(String query) async {
    final payload = await _client.getJson('/v1/search', query: {'q': query});
    return (payload['results'] as List? ?? const [])
        .whereType<Map>()
        .map((e) => LegalSearchResult.fromJson(e.cast<String, dynamic>()))
        .toList(growable: false);
  }

  @override
  Future<LegalDocument?> documentById(String codoId) async {
    final payload = await _client.getJson('/v1/documents/${Uri.encodeComponent(codoId)}');
    final data = payload['document'];
    return data is Map ? LegalDocument.fromJson(data.cast<String, dynamic>()) : null;
  }

  @override
  Future<DocumentProvenance?> documentProvenance(String codoId) async {
    final payload = await _client.getJson('/v1/documents/${Uri.encodeComponent(codoId)}/provenance');
    return DocumentProvenance.fromJson(payload);
  }

  @override
  Future<PublicationReceipt?> documentPublicationReceipt(String codoId) async {
    try {
      final payload = await _client.getJson('/v1/documents/${Uri.encodeComponent(codoId)}/publication-receipt');
      return PublicationReceipt.fromJson(payload);
    } on ApiException catch (error) {
      if (error.statusCode == 404) return null;
      rethrow;
    }
  }

  @override
  Future<List<LegalRelationship>> documentRelationships(String codoId) async {
    final payload = await _client.getJson('/v1/legal/documents/${Uri.encodeComponent(codoId)}/relationships');
    final items = payload['items'];
    if (items is List) {
      return items
          .whereType<Map>()
          .map((e) => LegalRelationship.fromJson(e.cast<String, dynamic>()))
          .toList(growable: false);
    }
    return const [];
  }

  @override
  Future<LegalArticle?> articleById(String codoId) async {
    final payload = await _client.getJson('/v1/articles/${Uri.encodeComponent(codoId)}');
    final data = payload['article'];
    return data is Map ? LegalArticle.fromJson(data.cast<String, dynamic>()) : null;
  }

  @override
  Future<List<LegalArticleVersion>> articleHistory(String codoId) async {
    final payload = await _client.getJson('/v1/articles/${Uri.encodeComponent(codoId)}/versions');
    return (payload['versions'] as List? ?? const [])
        .whereType<Map>()
        .map((e) => LegalArticleVersion.fromJson(e.cast<String, dynamic>()))
        .toList(growable: false);
  }
}

class HttpCodoAiRepository implements CodoAiRepository {
  HttpCodoAiRepository(this._client);

  final ApiClient _client;

  @override
  Future<CodoAnswer> answer(String question, {CodoAnswerMode mode = CodoAnswerMode.simple}) async {
    final payload = await _client.postJson('/v1/ai/answer', {'question': question, 'mode': mode.apiValue});
    final answer = CodoAnswer.fromJson(payload);
    if (!answer.hasSufficientVerifiedSources || answer.citations.isEmpty) {
      throw const VerifiedSourceUnavailable();
    }
    return answer;
  }
}
