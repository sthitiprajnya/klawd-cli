## 2024-11-20 - Accessible Truncated Text
**Learning:** When visually truncating text in the UI (e.g., using ellipses like `...` via JavaScript `substring` or CSS `text-overflow`), it creates an accessibility issue where the full content is hidden from screen readers and mouse users.
**Action:** Always pair visually truncated text with an accessible `title` attribute or a tooltip containing the full text to ensure accessibility and usability, as implemented for job IDs and tasks in `app.js`.

## 2024-11-20 - Semantic Tags and Scrollable Regions
**Learning:** Elements with scrollable regions (e.g., `overflow-x: auto` on `<pre>`) need to be focusable via `tabindex="0"` and labelled using `aria-labelledby` for screen reader accessibility. Also, using semantic HTML tags like `<main>` and `<header>` improves document structure over generic `<div>` elements. And dynamically updated elements should have `aria-live="polite"` so screen readers read the update.
**Action:** Replace structural `<div>` elements with `<main>` and `<header>`, add `tabindex="0"` and `aria-labelledby` to scrollable containers, and `aria-live="polite"` to dynamically updated elements.
