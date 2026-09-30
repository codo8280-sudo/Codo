import '../../domain/models/legal_models.dart';
import '../../domain/repositories/legal_repositories.dart';

class UnconfiguredLegalCorpusRepository implements LegalCorpusRepository {
  const UnconfiguredLegalCorpusRepository();

  @override
  Future<LegalArticle?> articleById(String codoId) async => null;

  @override
  Future<LegalDocument?> documentById(String codoId) async => null;

  @override
  Future<DocumentProvenance?> documentProvenance(String codoId) async => null;

  @override
  Future<PublicationReceipt?> documentPublicationReceipt(String codoId) async => null;

  @override
  Future<List<LegalRelationship>> documentRelationships(String codoId) async => const [];

  @override
  Future<List<LegalArticleVersion>> articleHistory(String codoId) async => const [];

  @override
  Future<List<LegalSearchResult>> search(String query) async => const [];
}

class UnconfiguredCodoAiRepository implements CodoAiRepository {
  const UnconfiguredCodoAiRepository();

  @override
  Future<CodoAnswer> answer(String question, {CodoAnswerMode mode = CodoAnswerMode.simple}) {
    throw const VerifiedSourceUnavailable();
  }
}
