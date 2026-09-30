import 'package:flutter/material.dart';

import '../design/codo_colors.dart';

class SourceRequiredCard extends StatelessWidget {
  const SourceRequiredCard({super.key, this.detail});

  final String? detail;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: CodoColors.softSurface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: CodoColors.quietBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.verified_outlined, color: CodoColors.civicGreen),
              SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Source juridique requise',
                  style: TextStyle(fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            'CODO ne dispose pas actuellement d une source verifiee suffisante pour confirmer ce point.',
          ),
          if (detail != null) ...[
            const SizedBox(height: 8),
            Text(detail!, style: Theme.of(context).textTheme.bodySmall),
          ],
        ],
      ),
    );
  }
}
