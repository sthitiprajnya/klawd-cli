## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Dynamic Content & Scrollable Regions
**Learning:** Elements with scrollable regions (e.g., `<pre>` with `overflow: auto`) are not accessible to keyboard-only users unless explicitly made focusable. Also, dynamically updated UI elements fail to announce changes to screen readers unless configured with `aria-live`.
**Action:** Always add `tabindex="0"` and an `aria-labelledby` attribute to scrollable regions, and use `aria-live="polite"` for dynamically updated containers like job lists or log outputs to ensure keyboard and screen reader accessibility.
