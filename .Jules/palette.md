## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Keyboard Accessible Scrollable Regions
**Learning:** Elements with scrollable content (like pre blocks with overflow auto) are inaccessible to keyboard users unless they can receive focus, and screen readers need to know what the region contains.
**Action:** Always add tabindex="0" to scrollable elements so they are focusable via keyboard, and pair them with an appropriate aria-labelledby attribute pointing to a heading to provide context.
