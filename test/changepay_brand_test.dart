import 'package:changepay_theme/changepay_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

double _contrast(Color a, Color b) {
  final la = a.computeLuminance(), lb = b.computeLuminance();
  final hi = la > lb ? la : lb, lo = la > lb ? lb : la;
  return (hi + 0.05) / (lo + 0.05);
}

void main() {
  test('every product resolves light and dark colors with AA text contrast', () {
    for (final product in CpProduct.values) {
      for (final b in Brightness.values) {
        final c = CpColors.of(product, b);
        expect(_contrast(c.text, c.bg), greaterThanOrEqualTo(4.5), reason: '$product $b text');
        expect(_contrast(c.onPrimary, c.primary), greaterThanOrEqualTo(4.5), reason: '$product $b primary');
      }
    }
  });

  test('product primaries match the logo-derived scales', () {
    expect(CpColors.of(CpProduct.consumer, Brightness.light).primary, CpPalette.indigo600);
    expect(CpColors.of(CpProduct.seller, Brightness.light).primary, CpPalette.sunset600);
    expect(CpColors.of(CpProduct.delivery, Brightness.light).primary, CpPalette.plum600);
    expect(CpGradient.product(CpProduct.consumer).colors, const [Color(0xFF381987), Color(0xFF01AAA5)]);
  });

  test('type scale sits on a 4px line grid and uses the bundled fonts', () {
    for (final s in [CpType.display, CpType.h1, CpType.body, CpType.caption, CpType.amount]) {
      expect((s.fontSize! * s.height!) % 4, 0);
      expect(s.fontFamily, contains('changepay_theme'));
    }
  });

  testWidgets('CpTheme builds and exposes CpColors as a ThemeExtension', (tester) async {
    late CpColors read;
    await tester.pumpWidget(MaterialApp(
      theme: CpTheme.build(CpProduct.seller),
      darkTheme: CpTheme.build(CpProduct.seller, Brightness.dark),
      home: Builder(builder: (context) {
        read = Theme.of(context).extension<CpColors>()!;
        return FilledButton(onPressed: () {}, child: const Text('Pay'));
      }),
    ));
    expect(read.primary, CpPalette.sunset600);
    expect(CpMotion.adaptive(tester.element(find.byType(FilledButton)), CpMotion.slow), CpMotion.slow);
  });
}
