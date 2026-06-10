## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Scrollable Region Focus and Dynamic Announcements
**Learning:** Elements with scrollable content (like `overflow: auto` in `<pre>` tags) are not naturally keyboard accessible, and dynamically updating content (like lists populated via JS) is missed by screen readers unless explicitly marked.
**Action:** Always add `tabindex="0"`, `:focus-visible` styles, and proper `aria-labelledby` labels to scrollable regions. Use `aria-live="polite"` on dynamic content containers to ensure accessibility.
