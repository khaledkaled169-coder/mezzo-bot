# Palette's Journal - Critical Learnings

## 2026-07-16 - Dynamic Onboarding & Tap-to-Copy UX
**Learning:** Telegram mobile clients allow users to tap monospace text (wrapped in backticks) to immediately copy details to clipboard. Dynamic text inserted into backtick blocks should have internal backticks sanitized to prevent entity parsing breakages.
**Action:** Wrap critical user friction numbers (account numbers, phone numbers, deposit amounts) in monospace backticks and sanitize dynamic user input before rendering.
