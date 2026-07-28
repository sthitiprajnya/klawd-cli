## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Dynamic Scrollable Regions
**Learning:** In dashboards displaying live-updating logs or code snippets (like skills and provenance data) within scrollable containers, mouse users can scroll implicitly, but keyboard users are trapped. Additionally, screen readers are unaware when this content updates.
**Action:** Always add `tabindex="0"` to scrollable elements (e.g., `<pre>` blocks with `overflow: auto`) and explicitly link them to their headings using `aria-labelledby`. Ensure dynamic containers use `aria-live="polite"` so async updates are properly announced.
