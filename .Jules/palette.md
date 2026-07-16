## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Semantic HTML and Accessible Regions
**Learning:** Generic tags like `<div>` lack semantic meaning for screen readers. Scrollable regions like `<pre>` without focusability or labels are inaccessible to keyboard and screen reader users. Dynamic content updates are easily missed without proper ARIA attributes.
**Action:** Prefer semantic HTML tags (`<main>`, `<header>`). Add `tabindex="0"` and an `aria-label` to scrollable regions. Use `aria-live="polite"` on containers where content updates dynamically.
