# XIB Reference

What a XIB is, how FutureBasic loads one, how Imagery LogicBank Studio for FutureBasic writes
them, and how to check one. Apple has **never published a XIB schema**: the format is
Interface Builder's XML archive of an object graph, and the rules below come from Apple's
guides, FB's reference, and what our own XIBs have taught us (each marked).

## 1. XIB and nib

- A **XIB** (`.xib`) is the development-time, XML form of a **nib**. Xcode (Interface Builder
  is built into it) compiles it to a binary `.nib` that goes into the app bundle; FB does the
  same when it builds a project that lists the XIB as a resource. ([Apple: Interface Builder Basic Concepts][ibbasics])
- The format has versions (3.0, 3.2, …); newer versions are more compact. Apple's position has
  long been that XIBs are not meant to be merged or edited by hand ([IB release notes][ibrn],
  [cocoa-dev 2007][xibfmt]). We generate them anyway — so every generated XIB must open cleanly
  in Xcode and pass `ibtool` (§5).
- "When you load a nib file at runtime, you get an exact replica of the objects that were in
  your Xcode document." ([Apple: Nib Files][nibs])

## 2. What is inside — the object graph

Every XIB we write and read has this shape (our generated Form part, trimmed):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<document type="com.apple.InterfaceBuilder3.Cocoa.XIB" version="3.0" toolsVersion="22146"
          targetRuntime="MacOSX.Cocoa" propertyAccessControl="none" useAutolayout="YES">
    <dependencies>
        <plugIn identifier="com.apple.InterfaceBuilder.CocoaPlugin" version="22146"/>
    </dependencies>
    <objects>
        <customObject id="-2" userLabel="File's Owner"/>
        <customObject id="-1" userLabel="First Responder" customClass="FirstResponder"/>
        <customObject id="-3" userLabel="Application" customClass="NSObject"/>
        <customView id="frm-1">                                <!-- the top-level view -->
            <rect key="frame" x="0.0" y="0.0" width="560" height="320"/>
            <autoresizingMask key="autoresizingMask" widthSizable="YES" heightSizable="YES"/>
            <subviews>
                <textField tag="101" id="frm-2"> … <textFieldCell key="cell" …/> </textField>
            </subviews>
        </customView>
    </objects>
</document>
```

- **Placeholders** (`id` -2, -1, -3): File's Owner, First Responder, Application. "The File's
  Owner object is a placeholder object that is not created when the nib file is loaded"; it is
  "the controller object that is responsible for the contents of the nib file". "The First
  Responder placeholder acts as a stand-in target for any action messages that need to be
  directed at the application's responder chain." Placeholders are not top-level objects. ([nibs])
- **Top-level objects** are "the subset of these objects that do not have a parent object" —
  windows, menu bars, views, controllers. ([nibs])
- **ids** are unique strings within one document (Xcode writes `abc-12-xyz`; ours are readable,
  e.g. `ps-abt-txt`). Connections and `headerView="…"` refer to them. *(ours: a duplicate id
  breaks the file — `xiblint`-style checks below)*
- **tags** (`tag="101"`) are how FB finds a control: `ControlSetStringValue( 101, … )`. They are
  ours to choose; the generator assigns them per entity (`Model Tags.incl`).
- **Cells:** older AppKit controls keep their look in a `…Cell key="cell"` child (title, font,
  colours, line break mode). The control's `tag` sits on the control, not the cell.
- **Colours** are catalog colours (`<color key="textColor" name="labelColor" catalog="System"
  colorSpace="catalog"/>`), so light and dark mode follow by themselves. *(ours: never write RGB
  values — the themes depend on it)*
- **Fonts:** `metaFont="system"`, `metaFont="smallSystem"`, `textStyle="largeTitle"`, or
  `usesAppearanceFont="YES"`.

## 3. Geometry and resizing

- `<rect key="frame" x y width height/>` is in the **superview's coordinates, origin at the
  bottom left** (AppKit's default, not flipped). *(ours: every layout bug so far was a top/bottom mix-up)*
- **Springs and struts:** `<autoresizingMask key="autoresizingMask" …/>` with `widthSizable`,
  `heightSizable`, `flexibleMinX` (left margin grows), `flexibleMaxX` (right margin grows),
  `flexibleMinY` (bottom margin grows: the view stays near the **top**), `flexibleMaxY`
  (stays near the bottom). The masks we use: `features/RESPONSIVE_LAYOUT_FEATURE.md`.
- `translatesAutoresizingMaskIntoConstraints="NO"` with `fixedFrame="YES"` is how Xcode writes a
  view laid out by frame; we do not use Auto Layout constraints.
- A view-based **table** is a `scrollView` → `clipView` → `tableView` (with `tableColumns`,
  each holding a `prototypeCellViews` / `tableCellView` whose `identifier` matches the column),
  plus `scroller`s and a `tableHeaderView`. FB keys rows by **column identifier**.

## 4. Loading XIBs in FutureBasic

| Statement | Loads |
|---|---|
| `nibwindow tag, nibName [, identifier]` | a window (the first one, or the one with that identifier) |
| `nibview tag, nibName [, identifier [, origin [, superviewTag]]]` | a view — **into another view** with `superviewTag` (tabs, panes); the first NSView unless `identifier` picks one |
| `nibtoolbar tag, nibName` / `nibmenu nibName` / `nibpopover tag, nibName` | a toolbar, a menu, a popover |

(`nibview.html`, `nibwindow.html`, … in FutureBasic_Documentation's `FBHelp`.)

- The tag given to `nibview` becomes the **view's** tag; the controls inside keep the tags in
  the XIB. Tags must be unique among the window's existing widgets.
- Configure after loading: "If you need to configure the objects in your nib file further at
  load time, the most appropriate time to do so is after your nib-loading call returns." ([nibs])
  *(ours: `FitPageView`, `ApplyBranding` and `RecentProjectsShow` run right after the `nibview`s)*
- Each load "creates a new copy of the objects" ([nibs]) — load a part once and show / hide it.

## 5. Checking a XIB

On a Mac with Xcode (Interface Builder's command-line compiler):

```bash
xcrun ibtool --errors --warnings --notices --output-format human-readable-text MyView.xib
```

```bash
xcrun ibtool --compile /tmp/MyView.nib MyView.xib
```

The first reports problems (by default as a plist with `com.apple.ibtool.document.errors` /
`.warnings` / `.notices`); the second compiles, as a build would. Sources: the ibtool man page
([unix.com copy][ibtool], [manpagez][ibtoolz]); options vary by Xcode version — `xcrun ibtool --help`
on your Mac is the authority. Chromium's build runs ibtool with exactly these three flags
([compile_xib.py][chromium]). An Apple forum thread notes ibtool can stay silent about warnings
Xcode shows ([forums][ibforum]) — opening the XIB in Xcode remains the final check.

Here (no Xcode): every XIB is parsed as XML before it is committed, and ids are checked for
duplicates. *(Backlog: a `tools/xiblint.py` — unique ids, connections that resolve, tags unique
per document, frames inside their superview, base64 key equivalents.)*

## 6. Rules we follow when writing XIBs (learned here)

- Key equivalents for Return and Escape are stored **base64** (`<string key="keyEquivalent"
  base64-UTF8="YES">DQ</string>`, `Gw`): `&#13;` / `&#27;` are not valid XML.
- The top-level view of a page part is `widthSizable heightSizable`; the code sizes it to its
  area (`FitPageView`) and its subviews' masks do the rest.
- Generated parts use catalog colours and system fonts only; nothing hard-coded.
- One part per XIB, named for what it is (`<Entity>Form.xib`, `<Entity>List.xib`,
  `ProjectSettingsView.xib`) — as Apple advises: "Store repeated user-interface components …
  in separate nib files", and design them "with lazy loading in mind". ([nibs])

[nibs]: https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/LoadingResources/CocoaNibs/CocoaNibs.html
[ibbasics]: https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/IB_UserGuide/ApplicationBasics/ApplicationBasics.html
[ibrn]: https://developer.apple.com/library/archive/releasenotes/DeveloperTools/RN-InterfaceBuilder/index.html
[xibfmt]: https://lists.apple.com/archives/cocoa-dev/2007/Dec/msg00495.html
[ibtool]: https://www.unix.com/man-page/osx/1/ibtool/
[ibtoolz]: https://www.manpagez.com/man/1/ibtool
[chromium]: https://chromium.googlesource.com/chromium/src/+/52.0.2743.116/build/config/mac/compile_xib.py
[ibforum]: https://developer.apple.com/forums/thread/66195
