## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Scrollable Regions & Dynamic Updates
**Learning:** Native scrolling regions (`overflow: auto` or `overflow-x: auto`) like `<pre>` blocks fail to support keyboard scrolling unless they are explicitly focusable, restricting accessibility for non-mouse users. Furthermore, dynamic dashboards injecting new content silently omit context for screen reader users.
**Action:** Always make scrollable elements focusable with `tabindex="0"`, pair them with visible `:focus-visible` styles and `aria-labelledby`, and ensure dynamic data containers utilize `aria-live="polite"` to responsibly broadcast updates.
