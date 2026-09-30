import 'package:flutter/material.dart';

import '../../domain/models/legal_models.dart';
import '../design/codo_colors.dart';

class LegalStatusBadge extends StatelessWidget {
  const LegalStatusBadge({super.key, required this.status});

  final LegalStatus status;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: status == LegalStatus.inForce ? CodoColors.softSurface : CodoColors.pureSurface,
        borderRadius: BorderRadius.circular(9),
        border: Border.all(color: CodoColors.quietBorder),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            status == LegalStatus.inForce ? Icons.verified_outlined : Icons.info_outline_rounded,
            size: 16,
            color: CodoColors.civicGreen,
          ),
          const SizedBox(width: 6),
          Text(status.label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}
