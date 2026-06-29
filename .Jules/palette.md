## 2026-06-16 - [Monospace formatting for copyable data]
**Learning:** In Telegram bots, using monospace formatting (backticks) for financial details, account numbers, and phone numbers is a high-impact micro-UX improvement because it enables "tap-to-copy" functionality, reducing user effort and errors during transactions.
**Action:** Always wrap numerical identifiers, transaction IDs, and account numbers in monospace backticks when using Markdown.

## 2026-06-16 - [Safe Markdown rendering with esc() and clean_mono()]
**Learning:** Dynamic data like usernames and names can contain special characters (e.g., underscores) that break Telegram Markdown V1 parsing. Using a dedicated `esc()` helper for literal text and `clean_mono()` for data inside backticks ensures consistent rendering and prevents message delivery failures.
**Action:** Use `esc()` for dynamic strings in Markdown outside of monospace blocks, and `clean_mono()` to sanitize data placed inside backticks.
