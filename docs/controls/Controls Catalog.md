# Controls Catalog

Native macOS controls available to the generated apps, where FutureBasic wraps
them, and how ready each one is. Toolbox paths are under
`Toolboxes/Headers/CocoaUI/` in FutureBasic_Documentation; examples under
`FBExamples/`. Verify names in the headers before using them
(`docs/reference/FB Coding Rules.md`).

Status: **ready** — FB example exists, use as is · **build** — FB wraps the parts,
we write a small reusable `.incl` · **prototype** — no FB example; prove it in
Test_Xib_View before the generator emits it.

## Feedback

| Control | macOS piece | FB toolbox | Example | Status |
|---|---|---|---|---|
| Toast (in-app) | `NSVisualEffectView` that slides in and fades out | `VisualEffectView.incl`, `Animation.incl`, `AnimationContext.incl`, `CoreAnimation/` | — | build: `Toast.incl`, e.g. `fn ToastShow( message, seconds )` |
| Toast (system) | Notification Center banner | `UserNotifications/` (`UNUserNotificationCenterAddNotificationRequest`) | `Notifications/UserNotificationCenter` | ready |
| Popover | `NSPopover` — anchored bubble for hints and quick edits | `Popover.incl` (`PopoverInit`) | — | build |

## Shapes and grouping

| Control | macOS piece | FB toolbox | Example | Status |
|---|---|---|---|---|
| Pill box (tags) | `NSTokenField` — typed, deletable, draggable pills | `TokenField.incl` | `Views and Controls/TokenField` | ready |
| Pill (badge) | rounded-bezel button, or small rounded box | `ButtonSetBezelStyle`, `Box.incl` | `Views and Controls/Button`, `Box` | ready |
| Rounded corners | box with corner radius, or any view's layer | `BoxSetCornerRadius`, `BoxSetFillColor`, `BoxSetBorderWidth`; `ViewSetWantsLayer` + `CALayerSetCornerRadius`, `CALayerSetMasksToBounds`, `CALayerSetShadow…` | `Views and Controls/Box` | ready |

## Images and documents

| Control | macOS piece | FB toolbox | Example | Status |
|---|---|---|---|---|
| Image viewer (simple) | `NSImageView` (`imageview` statement) | `ImageView.incl` | `Views and Controls/ImageView` (3 demos, drag-and-drop) | ready |
| Image viewer (zoom, rotate) | ImageKit `IKImageView` | `ImageKit/` | `Views and Controls/IKImageView` | ready |
| PDF viewer | `PDFView` | `PDFKit/` | `Views and Controls/PDFView` (3 demos) | ready |
| PDF thumbnail strip | `PDFThumbnailView` linked to a `PDFView` | `PDFKit/PDFThumbnailView.incl` (`PDFThumbnailViewSetPDFView`) | — | build |
| File thumbnails (any type) | Quick Look Thumbnailing | `QuickLookThumbnailing/` (`QLThumbnailGeneratorGenerateBestRepresentationForRequest`) | — | build |
| Quick Look preview | `QLPreviewPanel` (space-bar style) | `QuickLookUI/` | — | build |
| Carousel | `NSCollectionView`, horizontal flow layout, Quick Look thumbnails as items; click opens the image / PDF viewer | `CollectionView/` (`CollectionViewSetContent`, `CollectionViewFlowLayoutSetScrollDirection` with `NSCollectionViewScrollDirectionHorizontal`, `CollectionViewFlowLayoutSetItemSize`) | — | **prototype** |

## How they reach generated apps

- **Form Control choices.** Each becomes an option in the designer's *Form Control*
  column (Type Mapping.incl): e.g. *Image*, *PDF*, *Tokens*, *Thumbnails*.
  Northwind's `Employee.PhotoPath` (a path stored as text) set to *Image* gets an
  image viewer on the form.
- **Theme properties.** Corner radius, shadow, fill and border are style
  properties a theme file sets (`docs/design/App Shell Design.md` → Styling and themes).
- **Reusable files.** Each *build* item becomes one aptly named runtime `.incl`
  (e.g. `Toast.incl`, `Carousel.incl`) copied into generated apps.
