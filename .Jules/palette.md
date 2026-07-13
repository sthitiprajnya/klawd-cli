## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Keyboard Accessible Scrollable Regions
**Learning:** Elements with scrollable content (e.g. `overflow-x: auto` on `<pre>` tags) must be made keyboard focusable and appropriately labeled so that users navigating via keyboard can scroll the content and understand what it is.
**Action:** Always add `tabindex="0"` and an appropriate ARIA label (e.g. `aria-label`) to elements with `overflow: auto` or `overflow-x: auto`.
