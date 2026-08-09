# Palette's Journal - Critical UX and Accessibility Learnings

## 2026-07-16 - Telegram Support Menu Link Clickability vs. Monospace Formatting
**Learning:** Wrapping a Telegram handle (e.g. `@mezzodeposite`) in monospace backticks inside Telegram Markdown V1 blocks prevents it from being a clickable, interactable link in many Telegram clients. Conversely, phone numbers (e.g. `+251712759695`) should be formatted in monospace to support tap-to-copy without losing accessibility.
**Action:** Always format support phone numbers inside backticks for tap-to-copy, but keep user handles and Telegram invite links unformatted outside backticks so they remain clickable links for seamless navigation.
