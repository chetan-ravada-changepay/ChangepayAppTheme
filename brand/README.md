# ChangePay Brand

One source of truth for the ChangePay look across **ConsumerApp, SellerApp, DeliveryApp, Cp-Console,
Event Dashboard, KampusKonnect and Menu2CpayCatalog** — Flutter, SwiftUI, Compose and React/Tailwind.

```
brand/
├── tokens/tokens.json        ← edit this (colors, type, spacing, radius, shadows, motion)
├── logo/                     ← generated SVGs (traced from logo/source/*.png — the apps' existing logo)
│   ├── changepay-logo*.svg   master logo: gradient / white / mono / on-dark
│   ├── changepay-mark*.svg   ribbon mark only
│   ├── product/<app>/        logo, mark, lockup (+descriptor), app-icon (white & filled)
│   └── source/               original PNGs copied from ConsumerApp / DeliveryApp / SellerApp
├── icons/                    89 icons copied as-is from ConsumerApp (58) + SellerApp (31): outline/ material/ (themeable) + payments/ social/ food/ changepay/ + sprite.svg + icons.json
├── fonts/                    Plus Jakarta Sans, Inter, JetBrains Mono (OFL) — ttf/ for apps, web/ woff2
├── dist/                     generated — never hand-edit
│   ├── web/                  changepay-tokens.css, changepay-fonts.css, tailwind-preset.cjs, tokens.resolved.json, fonts/
│   ├── ios/ChangepayBrand.swift
│   └── android/ChangepayBrand.kt
└── scripts/                  build.mjs (tokens → all platforms), build_logo.py, build_icons.py
```

## Rebuild

```bash
node brand/scripts/build.mjs            # tokens → web / iOS / Android / lib/changepay_brand.dart (fails on WCAG contrast misses)
node brand/scripts/build.mjs --check    # CI: contrast check only
pip install fonttools uharfbuzz pillow potracer numpy
python brand/scripts/build_logo.py      # logos (reads product gradients from tokens.json)
python brand/scripts/build_icons.py     # re-copy icons from ConsumerApp, then SellerApp (ConsumerApp wins on a name clash)
```

## Products

| Product | Scale | Logo gradient | Primary (light) |
|---|---|---|---|
| ConsumerApp (flagship) | indigo | `#381987 → #01AAA5` | `#45289D` |
| SellerApp | sunset | `#F65F4F → #FDA73B` | `#C9392A` |
| DeliveryApp | plum | `#750C6F → #ED0066` | `#8E1279` |
| Cp-Console | violet | `#3C2566 → #9478CB` | `#5F3A9F` |
| Event Dashboard | violet | `#5F3A9F → #3966E6` | `#5F3A9F` |
| KampusKonnect | blue | `#2450CC → #38BDF8` | `#2450CC` |
| Menu2CpayCatalog | rose | `#E1517D → #ED7325` | `#BE2F5C` |

Consumer / Seller / Delivery gradients are sampled from the logos those apps already ship. The gradient is
for the logo, splash, hero and app icon. **UI uses the solid primary** (it passes WCAG AA with white text; the
light end of a gradient does not).

## Use it

### Flutter (ConsumerApp, SellerApp, DeliveryApp)

```yaml
dependencies:
  changepay_theme:
    git: { url: <ChangepayAppTheme repo>, ref: <tag> }
```
```dart
import 'package:changepay_theme/changepay_theme.dart';

MaterialApp(
  theme: CpTheme.build(CpProduct.seller),
  darkTheme: CpTheme.build(CpProduct.seller, Brightness.dark),
);
final c = Theme.of(context).extension<CpColors>()!;   // c.primary, c.surface, c.textMuted …
Text('₹1,250', style: CpType.amountXl.copyWith(color: c.text));
Container(decoration: BoxDecoration(gradient: CpGradient.product(CpProduct.seller), borderRadius: BorderRadius.circular(CpRadius.lg), boxShadow: CpShadow.e2));
AnimatedContainer(duration: CpMotion.adaptive(context, CpMotion.base), curve: CpMotion.standardCurve);
```
Fonts ship in the package. The legacy `ChangepayTheme` / `AppThemeColors` API is unchanged, so you can migrate one screen at a time.

### SwiftUI (ConsumerAppIOS, SellerAppIOS)
Copy `dist/ios/ChangepayBrand.swift` and `fonts/ttf/*.ttf` into the target (add the fonts to `UIAppFonts`).
```swift
let c = CPColors.of(.consumer, dark: colorScheme == .dark)
Text("Pay").cpText(CPType.label).foregroundStyle(c.onPrimary)
  .frame(height: CPSize.button).background(c.primary, in: .rect(cornerRadius: CPRadius.md))
withAnimation(CPMotion.snappySpring) { … }
```

### Compose (ConsumerAppAndroid, SellerAppAndroid)
Copy `dist/android/ChangepayBrand.kt` (package `com.changepay.brand`) and the TTFs into `res/font/`, then once at startup:
`CpFonts.display = FontFamily(Font(R.font.plusjakartasans_bold, FontWeight.W700), …)`. Use `CpColors.of(CpProduct.SELLER, isSystemInDarkTheme())`, `CpType.body`, `CpMotion.Standard`.

### Web (Cp-Console, Event Dashboard, KampusKonnect, Menu2CpayCatalog, ConsumerWebApp)
Copy `dist/web/` into the app (e.g. `src/brand/`).
```css
@import "./brand/changepay-fonts.css";
@import "./brand/changepay-tokens.css";
```
```html
<html data-cp-product="kampus">              <!-- consumer|seller|delivery|console|events|kampus|menu -->
<html data-cp-product="console" data-theme="dark">   <!-- force a theme; omit to follow the OS -->
```
```js
// tailwind.config.js
module.exports = { presets: [require("./src/brand/tailwind-preset.cjs")], … }
// <button class="bg-primary text-on-primary hover:bg-primary-hover rounded-cp-md text-label h-12 shadow-cp-e1 transition duration-fast ease-cp-standard">
```
Plain CSS: `var(--cp-color-primary)`, `var(--cp-space-4)`, `var(--cp-shadow-e2)`, `.cp-h1`, `var(--cp-ease-emphasized)`.

Icons are the apps' own files (ConsumerApp, then SellerApp) with their original names. The `outline/` and `material/` icons use `currentColor`, so they
inherit `color`: `<svg><use href="/brand/icons/sprite.svg#cp-wallet"/></svg>`, or inline the SVG file. Payment, social, food
and coin icons keep their own colours. Need a new icon? Add it to the app first, then rerun `build_icons.py`. DeliveryApp has no vector icons, so it isn't a source.

## Rules (short)

- **Logo:** keep clear space of at least the height of the "C" on all sides. Minimum size is 96px wide for the full logo and 20px for the mark.
  Never recolor outside the product gradients, stretch, outline, add effects, or set the wordmark in a font.
  On photos or dark backgrounds use `-white` or `-on-dark`.
- **Color:** use semantic tokens (`primary`, `surface`, `textMuted`) in UI, not palette steps. Use at most one gradient per screen.
- **Type:** Plus Jakarta Sans for headings and amounts (tabular figures), Inter for everything else. All line heights sit on a 4px grid.
- **Spacing:** 4px base, using only steps from the scale. Radius: 12 for controls, 16 for cards, 24 for sheets and dialogs.
- **Motion:** 100–300ms for UI, 450–600ms only for moments (payment success). Use `standard` easing to move, `enter` to appear and `exit` to leave.
  Respect reduced motion: crossfade only, no shimmer or sparks.
