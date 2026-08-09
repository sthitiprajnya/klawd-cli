## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.
## 2024-11-20 - Semantic HTML and Keyboard Accessibility
**Learning:** Elements with scrollable regions (like `<pre>` blocks) require `tabindex="0"` and `aria-labelledby` to be keyboard accessible. Furthermore, generic `<div>` wrappers should be replaced with semantic elements like `<main>` and `<header>` for better document structure and screen reader support. Dynamic containers need `aria-live="polite"` to announce content updates.
**Action:** Use semantic HTML tags (`<main>`, `<header>`), add `tabindex="0"` to scrollable regions paired with native focus outlines, and use `aria-live` for async content updates.
