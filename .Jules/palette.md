## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-06-27 - Accessible Scrollable Regions
**Learning:** Elements with scrollable regions (e.g., `overflow: auto` or `overflow-x: auto`) must be focusable using `tabindex="0"` and have proper ARIA labeling (e.g., `aria-labelledby`) to be accessible for keyboard users.
**Action:** Always add `tabindex="0"` and an `aria-labelledby` attribute to scrollable containers, like `pre` tags for code or logs, to ensure they can be focused and announced correctly by screen readers.
