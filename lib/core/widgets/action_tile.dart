import 'package:flutter/material.dart';

import '../design/codo_colors.dart';

class ActionTile extends StatelessWidget {
  const ActionTile({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.emphasis = false,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final bool emphasis;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: emphasis ? CodoColors.civicGreen : CodoColors.pureSurface,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: onTap,
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: emphasis ? CodoColors.civicGreen : CodoColors.quietBorder,
            ),
          ),
          child: Row(
            children: [
              Icon(icon, color: emphasis ? Colors.white : CodoColors.civicGreen),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        color: emphasis ? Colors.white : CodoColors.legalInk,
                        fontWeight: FontWeight.w700,
                        fontSize: 17,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: TextStyle(
                        color: emphasis ? Colors.white70 : CodoColors.secondaryGraphite,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_rounded, color: emphasis ? Colors.white : CodoColors.legalInk),
            ],
          ),
        ),
      ),
    );
  }
}
