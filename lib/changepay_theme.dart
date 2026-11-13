library changepay_theme;

import 'package:flutter/material.dart';

export 'changepay_brand.dart';

part 'package:changepay_theme/color_scheme.dart';
part 'package:changepay_theme/theme_constants/theme_constants.dart';
part 'package:changepay_theme/theme_constants/consumer_primary_theme.dart';
part 'package:changepay_theme/theme_constants/merchant_primary_theme.dart';
part 'package:changepay_theme/theme_constants/delivery_primary_theme.dart';
part 'package:changepay_theme/theme_constants/color_constants.dart';
part 'package:changepay_theme/theme_data.dart';

// For now, we are using the theme data from consumer app only.
// Later we will modify this as per the requirement.

/*

To Create a new Theme =>

  1.  Add a new Value in enum THEME_TYPES. e.g. enum THEME_TYPES { LIGHT , DARK }

  2.  Create a new color class extending AppThemeColors. e.g. DarkThemeColors
  class DarkThemeColors with AppThemeColors {
    @override
    Color get primaryColor => const Color()
    ....
    @override
    Brightness get brightness => Brightness.dark;
  }


To update theme =>
  CustomTheme.instanceOf(buildContext).changeTheme(key);

To access theme data =>

  for colors and text styles :
  color : CustomTheme.of(context).colors.primaryColor;
  style : CustomTheme.of(context).textStyles.headline6;
  otherwise
  appBarTheme : Theme.of(context).appBarTheme.

*/

class _ChangepayThemeInheritedWidget extends InheritedWidget {
  final _ChangepayThemeState data;

  _ChangepayThemeInheritedWidget({
    required this.data,
    Key? key,
    required Widget child,
  }) : super(key: key, child: child);

  @override
  bool updateShouldNotify(_ChangepayThemeInheritedWidget oldWidget) {
    return true;
  }
}

class ChangepayTheme extends StatefulWidget {
  final Widget child;
  final ChangepayThemeData changepayThemeData;

  const ChangepayTheme({
    Key? key,
    required this.changepayThemeData,
    required this.child,
  }) : super(key: key);

  @override
  _ChangepayThemeState createState() => new _ChangepayThemeState();

  // method to access the theme data
  static ChangepayThemeData of(BuildContext context) {
    _ChangepayThemeInheritedWidget? inherited = context
        .dependOnInheritedWidgetOfExactType<_ChangepayThemeInheritedWidget>();

    assert(inherited != null, 'No theme found in context');

    return inherited!.data.theme;
  }

  // method to update the theme data
  static _ChangepayThemeState instanceOf(BuildContext context) {
    _ChangepayThemeInheritedWidget? inherited = (context
        .dependOnInheritedWidgetOfExactType<_ChangepayThemeInheritedWidget>());

    assert(inherited != null, 'No theme found in context');

    return inherited!.data;
  }
}

class _ChangepayThemeState extends State<ChangepayTheme> {
  late final ChangepayThemeData _theme;
  ChangepayThemeData get theme => _theme;

  @override
  void initState() {
    _theme = widget.changepayThemeData;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return new _ChangepayThemeInheritedWidget(
      data: this,
      child: widget.child,
    );
  }
}
