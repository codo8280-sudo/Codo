import 'package:flutter/material.dart';

import '../../domain/models/legal_models.dart';
import '../design/codo_colors.dart';

class LegalSourceCard extends StatelessWidget {
  const LegalSourceCard({super.key, required this.source, this.articleLabel, this.version});

  final LegalSource source;
  final String? articleLabel;
  final String? version;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: CodoColors.pureSurface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: CodoColors.quietBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(source.trustLevel.label, style: const TextStyle(color: CodoColors.civicGreen, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text(source.name, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
          if (source.institutionName != null) Text(source.institutionName!, style: Theme.of(context).textTheme.bodySmall),
          if (articleLabel != null || version != null) ...[
            const SizedBox(height: 10),
            Text([articleLabel, version].whereType<String>().join(' • '), style: Theme.of(context).textTheme.bodySmall),
          ],
          if (source.probativeNote != null) ...[
            const SizedBox(height: 10),
            Text(source.probativeNote!, style: Theme.of(context).textTheme.bodySmall),
          ],
          const SizedBox(height: 12),
          SelectableText(source.url.toString(), style: const TextStyle(fontSize: 13)),
        ],
      ),
    );
  }
}
