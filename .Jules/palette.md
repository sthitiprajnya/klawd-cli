## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Keyboard Accessibility and Dynamic Announcements
**Learning:** Scrollable regions (`<pre>` tags with `overflow: auto`) are inaccessible to keyboard users if they lack a `tabindex="0"`. Additionally, dynamic content updates (like job queue and loaded JSON data) are not announced by screen readers without `aria-live` attributes.
**Action:** Always ensure elements with scrollable regions are focusable and correctly labeled with `aria-labelledby`, and ensure dynamic containers utilize `aria-live="polite"` so screen readers properly announce content updates.
