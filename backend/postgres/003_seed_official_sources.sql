begin;

insert into legal_sources (
  source_key, name, institution_name, official_url, trust_level, is_official,
  probative_note, verified_at, last_checked_at, terms_note
) values
  (
    'CI-SGG',
    'Secrétariat Général du Gouvernement',
    'Secrétariat Général du Gouvernement de Côte d’Ivoire',
    'https://web.sgg.gouv.ci/accueil',
    'A', true,
    'Le SGG assure notamment la publication au Journal officiel des actes législatifs et réglementaires dont la publication est autorisée.',
    '2026-09-29T00:00:00Z', '2026-09-29T00:00:00Z',
    'Respecter les conditions d’accès et de réutilisation de la source institutionnelle.'
  ),
  (
    'CI-JORCI',
    'Journaux Officiels de Côte d’Ivoire',
    'Secrétariat Général du Gouvernement / ONECI',
    'https://jorci.oneci.ci/',
    'A', true,
    'Plateforme officielle de consultation. Le SGG précise par ailleurs que seule la version originale du Journal officiel disponible dans ses locaux a valeur probante.',
    '2026-09-29T00:00:00Z', '2026-09-29T00:00:00Z',
    'Certains journaux récents peuvent être soumis à un accès payant ou conventionné ; CODO ne doit pas contourner ces modalités.'
  ),
  (
    'CI-CONSEIL-CONSTITUTIONNEL',
    'Conseil constitutionnel de Côte d’Ivoire',
    'Conseil constitutionnel',
    'https://www.conseil-constitutionnel.ci/',
    'A', true,
    'Source institutionnelle prioritaire pour la Constitution, les lois et décrets publiés par l’institution et les décisions du Conseil.',
    '2026-09-29T00:00:00Z', '2026-09-29T00:00:00Z',
    'Conserver la provenance exacte et la date de vérification de chaque document acquis.'
  ),
  (
    'CI-MJDH',
    'Ministère de la Justice et des Droits de l’Homme',
    'Ministère de la Justice et des Droits de l’Homme',
    'https://justice.gouv.ci/',
    'A', true,
    'Source institutionnelle pour textes juridiques, formulaires et procédures, décisions accessibles et cartographie judiciaire.',
    '2026-09-29T00:00:00Z', '2026-09-29T00:00:00Z',
    'Vérifier la date de publication et le statut de chaque contenu avant exploitation juridique.'
  ),
  (
    'OHADA-ACTES',
    'Actes uniformes OHADA',
    'Organisation pour l’Harmonisation en Afrique du Droit des Affaires',
    'https://www.ohada.org/actes-uniformes/',
    'A', true,
    'Source officielle prioritaire pour les Actes uniformes OHADA applicables dans les matières concernées.',
    '2026-09-29T00:00:00Z', '2026-09-29T00:00:00Z',
    'Conserver les références d’adoption, publication, entrée en vigueur et versions lorsqu’elles sont disponibles.'
  )
on conflict (source_key) do update set
  name = excluded.name,
  institution_name = excluded.institution_name,
  official_url = excluded.official_url,
  trust_level = excluded.trust_level,
  is_official = excluded.is_official,
  probative_note = excluded.probative_note,
  verified_at = excluded.verified_at,
  last_checked_at = excluded.last_checked_at,
  terms_note = excluded.terms_note,
  updated_at = now();

commit;
