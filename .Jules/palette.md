## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-05-24 - Scrollable Region Accessibility
**Learning:** Elements with scrollable regions (like `<pre>` tags with `overflow: auto`) are not keyboard accessible by default, meaning users navigating via keyboard cannot scroll to see hidden content.
**Action:** Always add `tabindex="0"` to scrollable containers and provide an accessible name via `aria-labelledby` referencing a visible heading, while relying on native browser focus outlines.
