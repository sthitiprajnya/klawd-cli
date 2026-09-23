## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-08-23 - Accessible Dynamic and Scrollable Content
**Learning:** Dynamic UI containers updated asynchronously via JavaScript must use `aria-live="polite"` to ensure screen readers announce updates. Additionally, elements with scrollable regions (like `<pre>` blocks with `overflow-x: auto`) are inaccessible to keyboard users unless they have `tabindex="0"` and are properly labeled with `aria-labelledby`.
**Action:** Always add `aria-live="polite"` to dynamic containers and ensure scrollable regions have `tabindex="0"` and `aria-labelledby` referencing their headings.
