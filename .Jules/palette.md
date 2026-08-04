## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-05-24 - Accessible Scrollable Regions
**Learning:** Elements with scrollable content (like `<pre>` blocks with `overflow-x: auto`) cannot be reached by keyboard users unless they are explicitly made focusable. This traps content for users who rely on keyboard navigation.
**Action:** Always add `tabindex="0"` and an appropriate `aria-labelledby` attribute to scrollable regions so they can receive focus and be properly announced by screen readers.
