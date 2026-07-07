## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-07-07 - Dynamic Updates and Scrollable Containers Accessibility
**Learning:** Containers that are dynamically updated via JavaScript must use `aria-live` attributes (like `aria-live="polite"`) to ensure screen readers announce content updates. Furthermore, scrollable regions (e.g., `overflow-x: auto`) must be focusable using `tabindex="0"` and have appropriate ARIA labeling (`aria-label` or `aria-labelledby`) so that keyboard users can navigate to and scroll them.
**Action:** Always include `aria-live="polite"` on dynamically changing content containers. Make all scrollable areas keyboard accessible with `tabindex="0"` and meaningful ARIA labels.
