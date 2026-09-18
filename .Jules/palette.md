## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Dynamic and Scrollable Regions
**Learning:** Dynamic UI containers that update asynchronously require `aria-live` attributes to notify screen readers. Additionally, scrollable regions (like `<pre>` blocks with `overflow: auto`) are inaccessible to keyboard users unless explicitly made focusable with `tabindex="0"` and labeled with `aria-labelledby`.
**Action:** Always wrap main content in semantic tags (`<main>`, `<header>`, `<section>`), use `aria-live="polite"` on async data containers, and ensure scrollable text blocks are keyboard focusable and properly labeled for screen readers.
