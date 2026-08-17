## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Keyboard Accessibility for Scrollable Regions
**Learning:** Elements with scrollable regions (e.g., `overflow: auto` or `overflow-x: auto`) like `<pre>` tags must be focusable using `tabindex="0"` and have visible focus styles and proper ARIA labeling (e.g., `aria-label`) to be accessible for keyboard users. Furthermore, dynamically updated containers (e.g., job lists) require `aria-live="polite"` to ensure screen readers properly announce content updates.
**Action:** Ensure all elements with `overflow: auto` are focusable and properly labeled, and dynamic containers use `aria-live` attributes to improve screen reader and keyboard accessibility.
