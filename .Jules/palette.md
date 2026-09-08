## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-21 - Accessible Scrollable Regions and Dynamic Content
**Learning:** Elements with scrollable regions (like <pre> tags) must be focusable using tabindex="0" and labeled with aria-labelledby. Additionally, dynamic UI containers updated via JS require aria-live="polite" for screen readers. Prefer semantic HTML elements like <main> and <header> over generic <div> wrappers.
**Action:** Always add tabindex="0" and aria-labelledby to scrollable regions, use aria-live="polite" for dynamic content, and use semantic HTML tags.
