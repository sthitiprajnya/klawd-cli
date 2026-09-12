## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2026-09-12 - Keyboard Accessibility for Scrollable Regions
**Learning:** Elements with scrollable regions (like <pre> tags with overflow-x: auto) are not accessible to keyboard users by default, preventing them from scrolling through the content.
**Action:** Always add tabindex="0" and an appropriate aria-labelledby attribute to scrollable containers to ensure they can receive focus and be scrolled using keyboard navigation.
