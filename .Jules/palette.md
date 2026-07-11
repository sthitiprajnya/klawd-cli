## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Scrollable Regions and Dynamic Updates Accessibility
**Learning:** Elements with scrollable regions (e.g., `overflow: auto`) must be focusable using `tabindex="0"` and have visible focus styles with proper ARIA labeling (e.g., `aria-labelledby`) to be accessible for keyboard users. Additionally, dynamic UI containers updated asynchronously (e.g., via JavaScript fetch) must use `aria-live` attributes (like `aria-live="polite"`) to ensure screen readers properly announce content updates. Furthermore, semantic HTML tags (like `<main>` and `<header>`) are essential for providing structural context to assistive technologies.
**Action:** Always verify scrollable regions have `tabindex="0"`, dynamic regions have `aria-live`, and rely on semantic HTML wrappers in place of generic `div` elements where appropriate.
