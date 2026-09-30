enum LegalStatus {
  inForce,
  partiallyInForce,
  amended,
  repealed,
  replaced,
  suspended,
  bill,
  draftDecree,
  adoptedAwaitingPublication,
  historical,
  verificationPending,
}

extension LegalStatusX on LegalStatus {
  String get label => switch (this) {
        LegalStatus.inForce => 'En vigueur',
        LegalStatus.partiallyInForce => 'Partiellement en vigueur',
        LegalStatus.amended => 'Modifié',
        LegalStatus.repealed => 'Abrogé',
        LegalStatus.replaced => 'Remplacé',
        LegalStatus.suspended => 'Suspendu',
        LegalStatus.bill => 'Projet de loi',
        LegalStatus.draftDecree => 'Projet de décret',
        LegalStatus.adoptedAwaitingPublication => 'Adopté, publication à vérifier',
        LegalStatus.historical => 'Historique',
        LegalStatus.verificationPending => 'En vérification',
      };

  String get apiValue => switch (this) {
        LegalStatus.inForce => 'in_force',
        LegalStatus.partiallyInForce => 'partially_in_force',
        LegalStatus.amended => 'amended',
        LegalStatus.repealed => 'repealed',
        LegalStatus.replaced => 'replaced',
        LegalStatus.suspended => 'suspended',
        LegalStatus.bill => 'bill',
        LegalStatus.draftDecree => 'draft_decree',
        LegalStatus.adoptedAwaitingPublication => 'adopted_awaiting_publication',
        LegalStatus.historical => 'historical',
        LegalStatus.verificationPending => 'verification_pending',
      };

  static LegalStatus parse(String? value) => switch (value) {
        'in_force' => LegalStatus.inForce,
        'partially_in_force' => LegalStatus.partiallyInForce,
        'amended' => LegalStatus.amended,
        'repealed' => LegalStatus.repealed,
        'replaced' => LegalStatus.replaced,
        'suspended' => LegalStatus.suspended,
        'bill' => LegalStatus.bill,
        'draft_decree' => LegalStatus.draftDecree,
        'adopted_awaiting_publication' => LegalStatus.adoptedAwaitingPublication,
        'historical' => LegalStatus.historical,
        _ => LegalStatus.verificationPending,
      };
}

enum SourceTrustLevel { officialPrimary, institutionalCopy, verifiedSecondary, unverified }

extension SourceTrustLevelX on SourceTrustLevel {
  String get code => switch (this) {
        SourceTrustLevel.officialPrimary => 'A',
        SourceTrustLevel.institutionalCopy => 'B',
        SourceTrustLevel.verifiedSecondary => 'C',
        SourceTrustLevel.unverified => 'D',
      };

  String get label => switch (this) {
        SourceTrustLevel.officialPrimary => 'Source officielle primaire',
        SourceTrustLevel.institutionalCopy => 'Reproduction institutionnelle',
        SourceTrustLevel.verifiedSecondary => 'Source secondaire vérifiée',
        SourceTrustLevel.unverified => 'Source non vérifiée',
      };

  static SourceTrustLevel parse(String? value) => switch (value) {
        'A' => SourceTrustLevel.officialPrimary,
        'B' => SourceTrustLevel.institutionalCopy,
        'C' => SourceTrustLevel.verifiedSecondary,
        _ => SourceTrustLevel.unverified,
      };
}

DateTime? _date(dynamic value) => value is String && value.isNotEmpty ? DateTime.tryParse(value) : null;
List<String> _strings(dynamic value) => value is List ? value.whereType<String>().toList(growable: false) : const [];

class LegalSource {
  const LegalSource({
    required this.id,
    required this.name,
    required this.trustLevel,
    required this.url,
    required this.isOfficial,
    this.institutionName,
    this.probativeNote,
    this.verifiedAt,
  });

  final String id;
  final String name;
  final SourceTrustLevel trustLevel;
  final Uri url;
  final bool isOfficial;
  final String? institutionName;
  final String? probativeNote;
  final DateTime? verifiedAt;

  factory LegalSource.fromJson(Map<String, dynamic> json) => LegalSource(
        id: '${json['id'] ?? json['source_key'] ?? ''}',
        name: json['name'] as String? ?? '',
        trustLevel: SourceTrustLevelX.parse(json['trust_level'] as String?),
        url: Uri.parse(json['url'] as String? ?? json['official_url'] as String? ?? ''),
        isOfficial: json['is_official'] as bool? ?? false,
        institutionName: json['institution_name'] as String?,
        probativeNote: json['probative_note'] as String?,
        verifiedAt: _date(json['verified_at']),
      );
}

class LegalDocument {
  const LegalDocument({
    required this.codoId,
    required this.title,
    required this.nature,
    required this.status,
    required this.source,
    this.number,
    this.adoptionDate,
    this.publicationDate,
    this.effectiveDate,
    this.currentVersion,
    this.authorityName,
  });

  final String codoId;
  final String title;
  final String nature;
  final String? number;
  final LegalStatus status;
  final LegalSource source;
  final DateTime? adoptionDate;
  final DateTime? publicationDate;
  final DateTime? effectiveDate;
  final String? currentVersion;
  final String? authorityName;

  factory LegalDocument.fromJson(Map<String, dynamic> json) => LegalDocument(
        codoId: json['codo_id'] as String? ?? '',
        title: json['title'] as String? ?? '',
        nature: json['nature'] as String? ?? '',
        number: json['number'] as String? ?? json['document_number'] as String?,
        status: LegalStatusX.parse(json['status'] as String? ?? json['current_status'] as String?),
        source: LegalSource.fromJson((json['source'] as Map?)?.cast<String, dynamic>() ?? const {}),
        adoptionDate: _date(json['adoption_date']),
        publicationDate: _date(json['publication_date']),
        effectiveDate: _date(json['effective_date']),
        currentVersion: json['current_version'] as String?,
        authorityName: json['authority_name'] as String?,
      );
}

class DocumentProvenanceSource {
  const DocumentProvenanceSource({
    required this.sourceId,
    required this.sourceName,
    required this.trustLevel,
    required this.provenanceRole,
    required this.sourceUrl,
    required this.capturedAt,
    required this.contentHash,
    this.institutionName,
    this.finalUrl,
    this.verifiedAt,
    this.note,
  });

  final String sourceId;
  final String sourceName;
  final String? institutionName;
  final SourceTrustLevel trustLevel;
  final String provenanceRole;
  final Uri sourceUrl;
  final Uri? finalUrl;
  final DateTime capturedAt;
  final String contentHash;
  final DateTime? verifiedAt;
  final String? note;

  factory DocumentProvenanceSource.fromJson(Map<String, dynamic> json) => DocumentProvenanceSource(
        sourceId: '${json['source_id'] ?? ''}',
        sourceName: json['source_name'] as String? ?? '',
        institutionName: json['institution_name'] as String?,
        trustLevel: SourceTrustLevelX.parse(json['trust_level'] as String?),
        provenanceRole: json['provenance_role'] as String? ?? 'verification',
        sourceUrl: Uri.parse(json['source_url'] as String? ?? ''),
        finalUrl: json['final_url'] is String ? Uri.tryParse(json['final_url'] as String) : null,
        capturedAt: _date(json['captured_at']) ?? DateTime.fromMillisecondsSinceEpoch(0, isUtc: true),
        contentHash: json['content_hash'] as String? ?? '',
        verifiedAt: _date(json['verified_at']),
        note: json['note'] as String?,
      );
}

class DocumentProvenance {
  const DocumentProvenance({required this.documentId, required this.versionKey, required this.sources});

  final String documentId;
  final String versionKey;
  final List<DocumentProvenanceSource> sources;

  factory DocumentProvenance.fromJson(Map<String, dynamic> json) => DocumentProvenance(
        documentId: json['document_id'] as String? ?? '',
        versionKey: json['version_key'] as String? ?? '',
        sources: (json['sources'] as List? ?? const [])
            .whereType<Map>()
            .map((e) => DocumentProvenanceSource.fromJson(e.cast<String, dynamic>()))
            .toList(growable: false),
      );
}

class PublicationReceipt {
  const PublicationReceipt({
    required this.documentId,
    required this.versionKey,
    required this.publicationHash,
    required this.sourceSnapshotHash,
    required this.publishedAt,
  });

  final String documentId;
  final String versionKey;
  final String publicationHash;
  final String sourceSnapshotHash;
  final DateTime publishedAt;

  factory PublicationReceipt.fromJson(Map<String, dynamic> json) => PublicationReceipt(
        documentId: json['document_id'] as String? ?? '',
        versionKey: json['version_key'] as String? ?? '',
        publicationHash: json['publication_hash'] as String? ?? '',
        sourceSnapshotHash: json['source_snapshot_hash'] as String? ?? '',
        publishedAt: _date(json['published_at']) ?? DateTime.fromMillisecondsSinceEpoch(0, isUtc: true),
      );
}

class LegalDocumentVersion {
  const LegalDocumentVersion({
    required this.versionKey,
    required this.status,
    required this.officialText,
    this.validFrom,
    this.validTo,
    this.isCurrent = false,
  });

  final String versionKey;
  final LegalStatus status;
  final String officialText;
  final DateTime? validFrom;
  final DateTime? validTo;
  final bool isCurrent;

  factory LegalDocumentVersion.fromJson(Map<String, dynamic> json) => LegalDocumentVersion(
        versionKey: json['version_key'] as String? ?? '',
        status: LegalStatusX.parse(json['status'] as String?),
        officialText: json['official_text'] as String? ?? '',
        validFrom: _date(json['valid_from']),
        validTo: _date(json['valid_to']),
        isCurrent: json['is_current'] as bool? ?? false,
      );
}

class LegalArticle {
  const LegalArticle({
    required this.codoId,
    required this.documentId,
    required this.label,
    required this.officialText,
    required this.status,
    required this.version,
    required this.source,
    this.explanation,
    this.shortSummary,
    this.validFrom,
    this.validTo,
  });

  final String codoId;
  final String documentId;
  final String label;
  final String officialText;
  final LegalStatus status;
  final String version;
  final LegalSource source;
  final String? explanation;
  final String? shortSummary;
  final DateTime? validFrom;
  final DateTime? validTo;

  factory LegalArticle.fromJson(Map<String, dynamic> json) => LegalArticle(
        codoId: json['codo_id'] as String? ?? '',
        documentId: json['document_id'] as String? ?? '',
        label: json['label'] as String? ?? json['article_label'] as String? ?? '',
        officialText: json['official_text'] as String? ?? '',
        status: LegalStatusX.parse(json['status'] as String?),
        version: json['version'] as String? ?? json['version_key'] as String? ?? '',
        source: LegalSource.fromJson((json['source'] as Map?)?.cast<String, dynamic>() ?? const {}),
        explanation: json['explanation_codo'] as String?,
        shortSummary: json['short_summary'] as String?,
        validFrom: _date(json['valid_from']),
        validTo: _date(json['valid_to']),
      );
}

class LegalArticleVersion {
  const LegalArticleVersion({
    required this.versionKey,
    required this.status,
    required this.officialText,
    this.validFrom,
    this.validTo,
    this.isCurrent = false,
  });

  final String versionKey;
  final LegalStatus status;
  final String officialText;
  final DateTime? validFrom;
  final DateTime? validTo;
  final bool isCurrent;

  factory LegalArticleVersion.fromJson(Map<String, dynamic> json) => LegalArticleVersion(
        versionKey: json['version_key'] as String? ?? '',
        status: LegalStatusX.parse(json['status'] as String?),
        officialText: json['official_text'] as String? ?? '',
        validFrom: _date(json['valid_from']),
        validTo: _date(json['valid_to']),
        isCurrent: json['is_current'] as bool? ?? false,
      );
}

enum CodoAnswerMode { simple, detailed, legal, professional }

extension CodoAnswerModeX on CodoAnswerMode {
  String get apiValue => switch (this) {
        CodoAnswerMode.simple => 'simple',
        CodoAnswerMode.detailed => 'detailed',
        CodoAnswerMode.legal => 'legal',
        CodoAnswerMode.professional => 'professional',
      };

  String get label => switch (this) {
        CodoAnswerMode.simple => 'Simple',
        CodoAnswerMode.detailed => 'Détaillé',
        CodoAnswerMode.legal => 'Juridique',
        CodoAnswerMode.professional => 'Professionnel',
      };

  static CodoAnswerMode parse(String? value) => switch (value) {
        'detailed' => CodoAnswerMode.detailed,
        'legal' => CodoAnswerMode.legal,
        'professional' => CodoAnswerMode.professional,
        _ => CodoAnswerMode.simple,
      };
}

class LegalCitation {
  const LegalCitation({
    required this.sourceId,
    required this.documentId,
    required this.version,
    this.articleId,
    this.label,
    this.sourceUrl,
    this.trustLevel,
  });

  final String sourceId;
  final String documentId;
  final String? articleId;
  final String version;
  final String? label;
  final Uri? sourceUrl;
  final String? trustLevel;

  factory LegalCitation.fromJson(Map<String, dynamic> json) => LegalCitation(
        sourceId: '${json['source_id'] ?? ''}',
        documentId: '${json['document_id'] ?? ''}',
        articleId: json['article_id']?.toString(),
        version: json['version'] as String? ?? '',
        label: json['label'] as String?,
        sourceUrl: json['source_url'] is String ? Uri.tryParse(json['source_url'] as String) : null,
        trustLevel: json['trust_level'] as String?,
      );
}

class LegalSearchResult {
  const LegalSearchResult({
    required this.document,
    this.article,
    required this.snippet,
    this.score,
    this.retrievalKind = 'lexical',
  });

  final LegalDocument document;
  final LegalArticle? article;
  final String snippet;
  final double? score;
  final String retrievalKind;

  factory LegalSearchResult.fromJson(Map<String, dynamic> json) => LegalSearchResult(
        document: LegalDocument.fromJson((json['document'] as Map).cast<String, dynamic>()),
        article: json['article'] is Map
            ? LegalArticle.fromJson((json['article'] as Map).cast<String, dynamic>())
            : null,
        snippet: json['snippet'] as String? ?? '',
        score: (json['score'] as num?)?.toDouble(),
        retrievalKind: json['retrieval_kind'] as String? ?? 'lexical',
      );
}

class CodoAnswer {
  const CodoAnswer({
    required this.situation,
    required this.lawSummary,
    required this.nextSteps,
    required this.citations,
    required this.hasSufficientVerifiedSources,
    this.documentsNeeded = const [],
    this.whereToAct = const [],
    this.deadlines = const [],
    this.attentionPoints = const [],
    this.answerMode = CodoAnswerMode.simple,
  });

  final String situation;
  final String lawSummary;
  final List<String> nextSteps;
  final List<LegalCitation> citations;
  final bool hasSufficientVerifiedSources;
  final List<String> documentsNeeded;
  final List<String> whereToAct;
  final List<String> deadlines;
  final List<String> attentionPoints;
  final CodoAnswerMode answerMode;

  factory CodoAnswer.fromJson(Map<String, dynamic> json) => CodoAnswer(
        situation: json['situation'] as String? ?? '',
        lawSummary: json['law_summary'] as String? ?? '',
        nextSteps: _strings(json['next_steps']),
        citations: (json['citations'] as List? ?? const [])
            .whereType<Map>()
            .map((e) => LegalCitation.fromJson(e.cast<String, dynamic>()))
            .toList(growable: false),
        hasSufficientVerifiedSources: json['has_sufficient_verified_sources'] as bool? ?? false,
        documentsNeeded: _strings(json['documents_needed']),
        whereToAct: _strings(json['where_to_act']),
        deadlines: _strings(json['deadlines']),
        attentionPoints: _strings(json['attention_points']),
        answerMode: CodoAnswerModeX.parse(json['answer_mode'] as String?),
      );
}

class LegalProcedure {
  const LegalProcedure({
    required this.id,
    required this.title,
    required this.summary,
    required this.steps,
    required this.citations,
  });

  final String id;
  final String title;
  final String summary;
  final List<ProcedureStep> steps;
  final List<LegalCitation> citations;
}

class ProcedureStep {
  const ProcedureStep({required this.order, required this.title, required this.description});

  final int order;
  final String title;
  final String description;
}

class Institution {
  const Institution({
    required this.id,
    required this.name,
    required this.type,
    this.competencies,
    this.address,
    this.contacts,
    this.officialUrl,
  });

  final String id;
  final String name;
  final String type;
  final String? competencies;
  final String? address;
  final String? contacts;
  final Uri? officialUrl;
}

class CaseLawDecision {
  const CaseLawDecision({
    required this.id,
    required this.jurisdiction,
    required this.date,
    required this.matter,
    this.number,
    this.legalQuestion,
    this.summary,
    this.source,
  });

  final String id;
  final String jurisdiction;
  final DateTime date;
  final String matter;
  final String? number;
  final String? legalQuestion;
  final String? summary;
  final LegalSource? source;
}

class LegalRelationship {
  const LegalRelationship({
    required this.id,
    required this.relationType,
    this.fromDocumentCodoId,
    this.fromArticleCodoId,
    this.toDocumentCodoId,
    this.toArticleCodoId,
    this.effectiveDate,
    this.evidenceSourceKey,
    this.evidenceSourceName,
    this.note,
  });

  final int id;
  final String? fromDocumentCodoId;
  final String? fromArticleCodoId;
  final String relationType;
  final String? toDocumentCodoId;
  final String? toArticleCodoId;
  final DateTime? effectiveDate;
  final String? evidenceSourceKey;
  final String? evidenceSourceName;
  final String? note;

  factory LegalRelationship.fromJson(Map<String, dynamic> json) => LegalRelationship(
        id: json['id'] as int? ?? 0,
        fromDocumentCodoId: json['from_document_codo_id'] as String?,
        fromArticleCodoId: json['from_article_codo_id'] as String?,
        relationType: json['relation_type'] as String? ?? '',
        toDocumentCodoId: json['to_document_codo_id'] as String?,
        toArticleCodoId: json['to_article_codo_id'] as String?,
        effectiveDate: _date(json['effective_date']),
        evidenceSourceKey: json['evidence_source_key'] as String?,
        evidenceSourceName: json['evidence_source_name'] as String?,
        note: json['note'] as String?,
      );
}
