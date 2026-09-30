import '../models/legal_models.dart';

abstract interface class LegalCorpusRepository {
  Future<List<LegalSearchResult>> search(String query);
  Future<LegalDocument?> documentById(String codoId);
  Future<DocumentProvenance?> documentProvenance(String codoId);
  Future<PublicationReceipt?> documentPublicationReceipt(String codoId);
  Future<List<LegalRelationship>> documentRelationships(String codoId);
  Future<LegalArticle?> articleById(String codoId);
  Future<List<LegalArticleVersion>> articleHistory(String codoId);
}

abstract interface class CodoAiRepository {
  Future<CodoAnswer> answer(String question, {CodoAnswerMode mode = CodoAnswerMode.simple});
}

class VerifiedSourceUnavailable implements Exception {
  const VerifiedSourceUnavailable([
    this.message = 'CODO ne dispose pas actuellement d’une source vérifiée suffisante pour confirmer ce point.',
  ]);

  final String message;

  @override
  String toString() => message;
}
