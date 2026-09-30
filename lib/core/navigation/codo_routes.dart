import 'package:flutter/material.dart';

import '../../features/admin/admin_workspace_screen.dart';
import '../../features/admin/audit_screen.dart';
import '../../features/admin/import_text_screen.dart';
import '../../features/admin/legal_validation_screen.dart';
import '../../features/admin/source_management_screen.dart';
import '../../features/admin/text_editor_screen.dart';
import '../../features/admin/version_management_screen.dart';
import '../../features/auth/auth_screen.dart';
import '../../features/institutions/institution_detail_screen.dart';
import '../../features/institutions/institutions_screen.dart';
import '../../features/jurisprudence/decision_detail_screen.dart';
import '../../features/jurisprudence/jurisprudence_screen.dart';
import '../../features/laws/article_history_screen.dart';
import '../../features/laws/article_screen.dart';
import '../../features/laws/code_explorer_screen.dart';
import '../../features/laws/laws_screen.dart';
import '../../features/laws/version_compare_screen.dart';
import '../../features/monitoring/legal_monitoring_screen.dart';
import '../../features/onboarding/onboarding_screen.dart';
import '../../features/pro/pro_advanced_search_screen.dart';
import '../../features/pro/pro_screen.dart';
import '../../features/procedures/procedure_detail_screen.dart';
import '../../features/settings/accessibility_screen.dart';
import '../../features/situations/situations_screen.dart';
import '../../features/space/alerts_screen.dart';
import '../../features/space/favorites_screen.dart';
import '../../features/space/folders_screen.dart';

abstract final class CodoRoutes {
  static const laws = '/laws';
  static const codeExplorer = '/laws/explorer';
  static const article = '/laws/article';
  static const articleHistory = '/laws/article/history';
  static const versionCompare = '/laws/article/compare';
  static const procedureDetail = '/procedures/detail';
  static const situations = '/situations';
  static const jurisprudence = '/jurisprudence';
  static const decisionDetail = '/jurisprudence/detail';
  static const institutions = '/institutions';
  static const institutionDetail = '/institutions/detail';
  static const monitoring = '/monitoring';
  static const favorites = '/space/favorites';
  static const alerts = '/space/alerts';
  static const folders = '/space/folders';
  static const pro = '/pro';
  static const proAdvanced = '/pro/search';
  static const auth = '/auth';
  static const onboarding = '/onboarding';
  static const accessibility = '/settings/accessibility';
  static const admin = '/admin';
  static const adminImport = '/admin/import';
  static const adminValidation = '/admin/validation';
  static const adminEditor = '/admin/editor';
  static const adminVersions = '/admin/versions';
  static const adminSources = '/admin/sources';
  static const adminAudit = '/admin/audit';

  static Route<dynamic>? onGenerateRoute(RouteSettings settings) {
    final builder = switch (settings.name) {
      laws => (_) => const LawsScreen(),
      codeExplorer => (_) => const CodeExplorerScreen(),
      article => (_) => ArticleScreen(codoId: settings.arguments as String?),
      articleHistory => (_) => ArticleHistoryScreen(codoId: settings.arguments as String?),
      versionCompare => (_) => const VersionCompareScreen(),
      procedureDetail => (_) => ProcedureDetailScreen(title: settings.arguments as String?),
      situations => (_) => const SituationsScreen(),
      jurisprudence => (_) => const JurisprudenceScreen(),
      decisionDetail => (_) => const DecisionDetailScreen(),
      institutions => (_) => const InstitutionsScreen(),
      institutionDetail => (_) => const InstitutionDetailScreen(),
      monitoring => (_) => const LegalMonitoringScreen(),
      favorites => (_) => const FavoritesScreen(),
      alerts => (_) => const AlertsScreen(),
      folders => (_) => const FoldersScreen(),
      pro => (_) => const ProScreen(),
      proAdvanced => (_) => const ProAdvancedSearchScreen(),
      auth => (_) => const AuthScreen(),
      onboarding => (_) => const OnboardingScreen(),
      accessibility => (_) => const AccessibilityScreen(),
      admin => (_) => const AdminWorkspaceScreen(),
      adminImport => (_) => const ImportTextScreen(),
      adminValidation => (_) => const LegalValidationScreen(),
      adminEditor => (_) => const LegalTextEditorScreen(),
      adminVersions => (_) => const VersionManagementScreen(),
      adminSources => (_) => const SourceManagementScreen(),
      adminAudit => (_) => const AuditScreen(),
      _ => null,
    };
    return builder == null ? null : MaterialPageRoute(builder: builder, settings: settings);
  }
}
