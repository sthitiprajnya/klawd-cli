## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-07-01 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Elements with scrollable regions (like `<pre>` with `overflow-x: auto`) cannot be reached by keyboard users unless they are explicitly made focusable, which breaks accessibility for screen readers and keyboard navigation. Additionally, dynamic UI sections that update asynchronously need proper attributes to announce their changes.
**Action:** Always add `tabindex="0"` and an `aria-labelledby` attribute (linking to a descriptive heading) to scrollable containers. For containers that dynamically load content via JS, apply `aria-live="polite"` so screen readers appropriately announce the updates.
