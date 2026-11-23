# Responsive Layout (generator window)

**Where:** `src/Generator/MainWindow.xib`, the page XIBs (`WelcomeView`, `NewProjectView`,
`ProjectCreateView`, `ProjectDetailView`, `ProjectSettingsView`), `Windows.incl`
(`PageFrame`, `FitPageView`), `My Globals.glbl` (`_minWindowWidth`, `_minWindowHeight`,
`_pageHeadingHeight`).

## How it works

```
+--------------+---------------------------------------------+
| Entity list  |  Project heading               (stretches)  |
| (top to      +---------------------------------------------+
|  bottom,     |                                             |
|  grows with  |  page view: fills the area, grows with the  |
|  the window  |  window in both directions                  |
|  height)     |                                             |
| [+][-]       |                                             |
+--------------+---------------------------------------------+
```

- **Window:** resizable, minimum content size 1000 × 620 (`WindowSetContentMinSize`, and
  `minSize` in the XIB).
- **Entity list:** fixed width (254), from 20 pt below the top edge to just above the
  +/− buttons; its height follows the window (`flexibleMaxX` + `heightSizable`).
- **Heading:** right of the list, pinned to the top, stretches across.
- **Pages:** `FitPageView` sets each page's frame to `PageFrame` (beside the list, below
  the heading) after the toolbar is set, with `NSViewWidthSizable + NSViewHeightSizable`.
  Inside each page the XIB's autoresizing masks place the controls:

| Kind of control | Mask | Examples |
|---|---|---|
| tables, page boxes | width + height sizable | attribute table, Recent Projects, Welcome box |
| entry fields | width sizable, top pinned | Project Name, Database path, About text |
| labels, titles | top-left pinned | page titles, field labels |
| Welcome / server form content | centred, top pinned | logo, Create Project, Open Project… |
| action buttons | bottom-right pinned | Create, Done; Cancel bottom-left on the server form |

## Decisions
- Springs and struts (autoresizing masks), not Auto Layout: the XIBs already use them,
  FB's `nibview` keeps them, and they're readable in the XML.
- Pages are sized in code once (`FitPageView`) so the XIBs can keep their design sizes.

## Verify on a Mac
- [ ] The window can't be made smaller than 1000 × 620
- [ ] The entity list runs from the top to the +/− buttons and grows/shrinks with the window
- [ ] Each page fills the width; tables grow in both directions; buttons stay in their corners
