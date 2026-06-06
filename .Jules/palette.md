## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-06-06 - Accessible Dynamic Content and Scrollable Regions
**Learning:** Dynamic UI containers updated asynchronously (e.g., job lists, skill loading) lack screen reader announcements by default, and elements with horizontal scroll (like `<pre>`) are inaccessible to keyboard users unless explicitly managed.
**Action:** Always add `aria-live="polite"` to dynamically updated containers, and ensure scrollable regions have `tabindex="0"`, an `aria-labelledby` for context, and visible `:focus-visible` styles to provide a fully accessible experience.
