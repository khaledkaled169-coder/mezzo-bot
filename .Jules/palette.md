## 2026-07-16 - Link Clickability versus Monospace Formatting
**Learning:** In Telegram Markdown blocks, wrapping text in monospace (backticks) blocks parses characters literally but prevents formatting processing. Importantly, wrapping links or Telegram handles inside monospace blocks prevents them from being clickable in many clients.
**Action:** Keep Telegram handles (e.g., `@mezzodeposite`) and URL links unformatted so they remain clickable, while using monospace backticks for purely textual identifiers or numeric codes like transaction IDs and phone numbers to allow easy tap-to-copy.
