## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Elements with scrollable regions (e.g., `overflow-x: auto` on `<pre>` tags for code blocks or JSON output) cannot be accessed by keyboard-only users unless they are explicitly made focusable. Furthermore, dynamically updating content areas need to announce their changes to screen readers.
**Action:** Always add `tabindex="0"` to scrollable containers and provide them an accessible name (e.g., via `aria-labelledby` pointing to a nearby heading) so keyboard users can focus and scroll them. Also, use `aria-live="polite"` on containers whose content is updated asynchronously (like job lists or fetched skills data) so screen readers can announce the updates.
