## 2026-06-16 - Initializing Palette UX Improvements
**Learning:** Telegram bots benefit significantly from consistent formatting (Bold for headers, Monospace for data) to improve readability and usability (tap-to-copy). Dynamic data must be sanitized/escaped for Markdown V1 to prevent parsing errors.
**Action:** Implementing `escape_md` and `clean_mono` helpers and applying them to balance and payment flows.
## 2026-06-16 - Technical Hygiene in UX PRs
**Learning:** UX improvements should not come at the cost of repository cleanliness. Binary files like `__pycache__` and unused helper functions (`escape_md`) clutter the codebase and fail production standards.
**Action:** Always verify the patch for accidental binary inclusions and remove dead code before submission.
