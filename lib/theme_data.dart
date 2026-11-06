// ignore_for_file: public_member_api_docs, sort_constructors_first
part of 'package:changepay_theme/changepay_theme.dart';

// Add a new value here for each new theme.

class ChangepayThemeData {
  // Creating custom colorScheme and textTheme
  // so that , we can use more meaningful names for colors and textstyles defined in theme data.
  // also we can avoid overriding the old screen's style variables while using dynamic values for new screens.
  final AppThemeColors colors;
  final AppTextStyles textStyles;
  final ThemeData themeData;
  ChangepayThemeData({
    required this.colors,
    required this.textStyles,
    required this.themeData,
  });
}
