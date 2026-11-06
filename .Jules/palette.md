# Palette's Journal - Mezzo Bot UX & Accessibility Learnings

## 2026-07-16 - Tap-to-Copy Monospace for Payment Instructions
**Learning:** In chat-based interfaces (like Telegram), copying account numbers and exact amounts is a major user friction point. Users frequently switch between banking apps (Telebirr, CBE) and Telegram. Formatting payment details (account number, phone number, amount) inside inline code backticks enables instant single-tap copying on mobile clients without capturing surrounding explanatory text.
**Action:** Always format account numbers, recipient phone numbers, and transactional amounts inside monospace backticks (`` `value` ``) and declare `parse_mode="Markdown"` when rendering payment guidance.
