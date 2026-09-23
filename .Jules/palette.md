## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-21 - Accessible Dynamic and Scrollable Regions
**Learning:** Dynamic UI containers and visually scrollable regions (`<pre>` blocks) are inaccessible to screen reader and keyboard users without explicit attributes.
**Action:** Always add `aria-live="polite"` to dynamic containers for announcements, and `tabindex="0"` with `aria-labelledby` to scrollable regions for keyboard navigation.
