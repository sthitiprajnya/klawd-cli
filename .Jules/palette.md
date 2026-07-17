## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Semantic HTML, aria-live, and Keyboard Focus for Accessibility
**Learning:** Generic `<div>` tags do not provide document structure information to assistive technologies. Dynamically updated content sections might be missed by screen readers if they lack `aria-live` regions. Additionally, elements with scrollable overflow must be keyboard focusable (`tabindex="0"`) and labeled for full accessibility.
**Action:** Use semantic HTML (`<main>`, `<header>`, `<section>`) for page structure. Add `aria-live="polite"` to containers that fetch data dynamically. Ensure scrollable regions like `<pre>` tags have `tabindex="0"` and an `aria-label` or `aria-labelledby` to make them accessible to screen readers and keyboard users.
