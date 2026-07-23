# Palette's Journal

## 2026-07-16 - State-Aware Command Routing
**Learning:** Hardcoded command responses like starting registration from scratch when user sends `/start` frustrates already registered users and adds redundant friction. Checking user state in the command handler and dynamically routing them provides a seamless, context-rich experience.
**Action:** Always check the user's database entry and registration/profile completeness when handling introductory commands, and route fully registered users directly to the main menu while prompting partially registered users for only their missing details.
