## 2026-06-16 - Telegram Markdown V1 Constraints
**Learning:** Telegram Markdown V1 does not process escapes inside monospace backticks (rendering backslashes literally), but requires them outside. Dynamic data inside backticks must have internal backticks removed rather than escaped.
**Action:** Use a `clean_mono` helper to strip backticks for monospace blocks and an `esc` helper for normal text to ensure reliable message parsing.
