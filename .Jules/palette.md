## 2026-07-16 - Telegram Support Monospace and Clickable Handles
**Learning:** Monospace formatting (`backticks`) in Telegram enables tap-to-copy functionality, which is ideal for numeric details (phone numbers, account IDs) but breaks clickability on user/channel handles (e.g. `@mezzodeposite`). To maintain optimal UX, handles must remain unformatted while phone numbers are monospace-wrapped.
**Action:** Keep Telegram handles as raw text while wrapping associated phone numbers/ID details in backticks with `parse_mode="Markdown"`.
