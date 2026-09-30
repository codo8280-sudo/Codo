import 'package:flutter/material.dart';

import 'codo_colors.dart';

abstract final class CodoTheme {
  static ThemeData light() {
    final scheme = ColorScheme.fromSeed(
      seedColor: CodoColors.civicGreen,
      brightness: Brightness.light,
      surface: CodoColors.pureSurface,
    ).copyWith(
      primary: CodoColors.civicGreen,
      onPrimary: Colors.white,
      surface: CodoColors.pureSurface,
      onSurface: CodoColors.legalInk,
      outline: CodoColors.quietBorder,
    );

    return ThemeData(
      useMaterial3: true,
      fontFamily: 'Geist',
      scaffoldBackgroundColor: CodoColors.ivoryCanvas,
      colorScheme: scheme,
      textTheme: const TextTheme(
        displaySmall: TextStyle(
          color: CodoColors.legalInk,
          fontSize: 40,
          height: 1.08,
          fontWeight: FontWeight.w700,
          letterSpacing: -1.2,
        ),
        headlineMedium: TextStyle(
          color: CodoColors.legalInk,
          fontSize: 28,
          height: 1.15,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.5,
        ),
        titleLarge: TextStyle(
          color: CodoColors.legalInk,
          fontSize: 20,
          height: 1.25,
          fontWeight: FontWeight.w600,
        ),
        bodyLarge: TextStyle(
          color: CodoColors.legalInk,
          fontSize: 18,
          height: 1.7,
        ),
        bodyMedium: TextStyle(
          color: CodoColors.legalInk,
          fontSize: 16,
          height: 1.65,
        ),
        bodySmall: TextStyle(
          color: CodoColors.secondaryGraphite,
          fontSize: 14,
          height: 1.5,
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: CodoColors.ivoryCanvas,
        foregroundColor: CodoColors.legalInk,
        elevation: 0,
        scrolledUnderElevation: 0,
        surfaceTintColor: Colors.transparent,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: CodoColors.pureSurface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: CodoColors.quietBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: CodoColors.civicGreen, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: CodoColors.legalInk),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: CodoColors.civicGreen,
          foregroundColor: Colors.white,
          minimumSize: const Size(0, 48),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: CodoColors.legalInk,
          minimumSize: const Size(0, 48),
          side: const BorderSide(color: CodoColors.quietBorder),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
        ),
      ),
      dividerColor: CodoColors.quietBorder,
    );
  }
}
