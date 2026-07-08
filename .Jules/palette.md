## 2026-06-16 - [Tap-to-copy formatting for critical data]
**Learning:** In Telegram bots, wrapping sensitive or actionable data (like account numbers or transaction amounts) in monospace backticks significantly improves UX by enabling 'tap-to-copy'. However, dynamic data inside these blocks must be sanitized to remove internal backticks to avoid parsing errors.
**Action:** Always use a helper like `clean_mono()` for data inside backticks and `esc()` for dynamic data in the rest of the message when using Markdown.
