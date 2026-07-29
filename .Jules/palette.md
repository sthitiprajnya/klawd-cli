## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2025-01-22 - Semantic HTML, ARIA labels and Focusable Scrollable Regions
**Learning:** Generic divs hurt document structure. In dynamic UIs, elements updating asynchronously require `aria-live="polite"` attributes to alert screen readers. Scrollable regions must be focusable using `tabindex="0"` and properly labeled using `aria-labelledby` to be fully accessible for keyboard users.
**Action:** Prefer semantic HTML (`<main>`, `<header>`), ensure dynamically updated elements use `aria-live="polite"`, and apply `tabindex="0"` alongside `aria-labelledby` to any scrollable element.
