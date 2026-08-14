## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Elements with scrollable regions (e.g., `overflow: auto` or `overflow-x: auto` on `<pre>` tags) must be focusable using `tabindex="0"` and have proper ARIA labeling (e.g., `aria-labelledby`) to be accessible for keyboard users. Furthermore, dynamically updated containers asynchronously populated via JavaScript must use `aria-live="polite"` attributes so screen readers properly announce content updates.
**Action:** Always verify scrollable text blocks and asynchronous data containers include necessary keyboard and ARIA attributes (like `tabindex="0"` and `aria-live="polite"`) and prefer semantic layout elements (`<main>`, `<section>`).
