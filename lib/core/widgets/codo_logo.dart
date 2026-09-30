import 'package:flutter/material.dart';

import '../design/codo_colors.dart';

class CodoLogo extends StatelessWidget {
  const CodoLogo({super.key, this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'CODO, Centre d Orientation du Droit et des Obligations',
      child: Text(
        'CODO',
        style: TextStyle(
          color: CodoColors.legalInk,
          fontSize: compact ? 22 : 28,
          fontWeight: FontWeight.w800,
          letterSpacing: -1.0,
        ),
      ),
    );
  }
}
