---
name: Cracker House x Snuggle Pop-up
colors:
  surface: '#fff8f5'
  surface-dim: '#f4d4c1'
  surface-bright: '#fff8f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff1ea'
  surface-container: '#ffeade'
  surface-container-high: '#ffe3d3'
  surface-container-highest: '#fddcc9'
  on-surface: '#28180c'
  on-surface-variant: '#58413f'
  inverse-surface: '#402c1f'
  inverse-on-surface: '#ffede4'
  outline: '#8b716e'
  outline-variant: '#dfbfbc'
  surface-tint: '#a8372f'
  primary: '#9b2d27'
  on-primary: '#ffffff'
  primary-container: '#bc453c'
  on-primary-container: '#ffecea'
  inverse-primary: '#ffb4ab'
  secondary: '#336289'
  on-secondary: '#ffffff'
  secondary-container: '#a7d3ff'
  on-secondary-container: '#2c5b82'
  tertiary: '#963500'
  on-tertiary: '#ffffff'
  tertiary-container: '#be4600'
  on-tertiary-container: '#ffede7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad6'
  primary-fixed-dim: '#ffb4ab'
  on-primary-fixed: '#410002'
  on-primary-fixed-variant: '#881f1a'
  secondary-fixed: '#cde5ff'
  secondary-fixed-dim: '#9ecbf7'
  on-secondary-fixed: '#001d32'
  on-secondary-fixed-variant: '#164a6f'
  tertiary-fixed: '#ffdbce'
  tertiary-fixed-dim: '#ffb598'
  on-tertiary-fixed: '#370e00'
  on-tertiary-fixed-variant: '#7e2c00'
  background: '#fff8f5'
  on-background: '#28180c'
  surface-variant: '#fddcc9'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 84px
    fontWeight: '900'
    lineHeight: 90px
    letterSpacing: -0.04em
  headline-xl:
    fontFamily: Playfair Display
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 52px
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 38px
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: Space Mono
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
spacing:
  grid-margin: 2rem
  gutter: 1rem
  block-gap: 2px
  section-padding: 4rem
---

## Brand & Style

The brand personality is an intentional collision between high-fashion editorial rigor and the comforting, utilitarian warmth of household laundry. It evokes a "Vintage Editorial" mood—nostalgic, grainy, and tactile—while maintaining the "Clean Laundry" freshness of the partnership.

The design style is **Editorial Brutalism**. It utilizes high-contrast typography and a rigid, block-based layout structure inspired by print magazines and film contact sheets. Raw textures, such as film grain and paper noise, are overlaid on crisp digital elements to bridge the gap between retro physical media and modern web commerce. The emotional response is one of sophisticated nostalgia: it feels like a found objects catalog that has been meticulously curated.

## Colors

The palette balances the fiery, energetic "Burnt Orange" of fashion-forward branding with the stabilizing, professional "Deep Brown" and "Muted Blue" of household reliability.

- **Primary Burnt Orange (#BC453C):** Used for key brand accents and primary calls to action.
- **Muted Blue (#517EA6):** Represents the "Clean Laundry" aspect, used for supporting UI elements and secondary buttons.
- **Deep Brown (#594335):** Acts as the primary "ink" color for typography and heavy structural borders.
- **Accent Orange (#F25C05):** Used sparingly for "New" tags or high-priority notifications.
- **Paper Background (#F9F6F1):** Instead of a pure white, a warm, off-white paper texture is used to reinforce the vintage editorial feel.

## Typography

Typography is the primary driver of the "Editorial" aesthetic. It relies on a high-contrast relationship between a dramatic serif and a functional sans-serif.

- **Headlines:** Use **Playfair Display**. It should be set with tight leading and negative letter-spacing for large display sizes to mimic 70s fashion mastheads.
- **Body Text:** Use **Hanken Grotesk**. It provides a clean, contemporary contrast to the serif headings, ensuring high legibility for product descriptions and logistical information.
- **Utility & Data:** Use **Space Mono** for labels, SKU numbers, and "laundry care" instructions. This monospaced choice reinforces the utilitarian "laundry detergent" side of the collaboration.

## Layout & Spacing

The layout follows a **Fixed Grid** philosophy based on a modular block structure. The design is inspired by "Contact Sheets" where content is housed in clearly defined, rectangular containers.

- **The Block System:** Sections are separated by a 2px "Deep Brown" border, creating a tactile grid of content blocks. Elements within blocks should have generous internal padding (min 24px) to prevent the design from feeling cluttered.
- **Verticality:** The mobile experience should feel like a continuous film strip, scrolling through distinct, full-width blocks.
- **Desktop Breakpoints:** On desktop, the grid expands to a 12-column layout. Images and text blocks should "snap" to the grid lines, often overlapping slightly to create the "magazine collage" effect.

## Elevation & Depth

This design system eschews traditional shadows in favor of **Tonal Layers** and **Structural Borders**. 

- **Flat Depth:** Depth is created by stacking colored blocks. A "Muted Blue" block may sit atop a "Paper" background, separated only by a 1px or 2px solid "Deep Brown" border.
- **Film Overlays:** To achieve the "Vintage Editorial" look, a global noise/grain texture should be applied to the entire background.
- **Interactive States:** Buttons and interactive cards do not lift; instead, they invert their colors or shift 4px down/right to reveal a solid color "shadow" block underneath, mimicking a physical stamp or print press.

## Shapes

The shape language is strictly **Sharp (0px)**. 

To maintain the architectural, block-based editorial feel, all containers, buttons, and image frames must have square corners. This emphasizes the "grid" and mimics the edges of printed photographs and magazine pages. The only exception is the use of circular "Stickers" or "Badges" that can be placed as floating overlays on images to highlight "Limited Edition" or "Sold Out" status, acting as a deliberate break from the rigid grid.

## Components

- **Buttons:** Solid "Deep Brown" background with "Paper" colored text in uppercase Mono. They should have a 1px solid border. Upon hover, the background shifts to "Burnt Orange."
- **Cards (The Block):** Every product or news item is contained within a block defined by a 2px "Deep Brown" border. Images inside cards should always have a slight "grain" filter.
- **Inputs:** Simple underlined fields using "Deep Brown." Labels should sit above the line in the "label-caps" typography style.
- **Film Strip Gallery:** A horizontal scroll component for images that includes "frame numbers" and "Kodak-style" edge markings in the margins, reinforcing the vintage photography theme.
- **Stickers:** Small, floating circular elements in "Accent Orange" used for promotional callouts, positioned slightly off-axis (rotated 5-10 degrees) to feel like they were hand-placed on the page.