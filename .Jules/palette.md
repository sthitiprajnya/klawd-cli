## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Keyboard Accessibility for Scrollable Elements and Dynamic UI Updates
**Learning:** Elements with scrollable regions (like `<pre>` blocks displaying raw JSON) can trap keyboard focus or become completely inaccessible to keyboard-only users if not explicitly made focusable. Furthermore, dynamic UI containers that load data asynchronously need ARIA announcements to inform screen reader users of updates.
**Action:** When working with `<pre>` blocks or other elements that use `overflow: auto` or `overflow-x: auto`, ensure they have `tabindex="0"`, a proper focus indicator (e.g., `:focus-visible`), and an ARIA association (like `aria-labelledby`). Additionally, apply `aria-live="polite"` to dynamic UI containers to gracefully announce asynchronous content changes.
