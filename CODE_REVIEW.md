# Code Review Report

## Scope
- Frontend shared layout, editor page, and API module comments.
- Quick build/install sanity check in current container.

## Findings

### 1) Shared layout still contains hardcoded UI copy (i18n inconsistency)
- **Severity:** Medium
- **Where:** `src/components/layout/Navbar.vue`
- **Details:** The shared navbar contains fixed English strings (`Premium UI Library`, `Switch to English`, `Switch to Chinese`) instead of i18n keys. This violates the repo guideline to avoid hardcoded Chinese/English in shared layout components and makes locale switching only partially translated.
- **Evidence:** `Navbar.vue` lines 8 and 30.
- **Suggestion:** Move these strings to `src/i18n` message bundles and use `t(...)` in template attributes/text.

### 2) Prompt editor has many hardcoded Chinese labels/placeholders
- **Severity:** Medium
- **Where:** `src/views/PromptEditor.vue`
- **Details:** The editor page uses large amounts of hardcoded Chinese copy for section titles, labels, placeholder text, and helper text. In English locale this page remains mostly Chinese, causing inconsistent UX compared with login/register pages that already use i18n.
- **Evidence:** `PromptEditor.vue` lines 29-37, 54-57, 89-98, 148-157, 166, 176.
- **Suggestion:** Extract all user-facing text to i18n keys and provide both `zh`/`en` values.

### 3) API module comments have encoding mojibake
- **Severity:** Low
- **Where:** `src/api/index.js`
- **Details:** Most comments are garbled (`鍒涘缓 axios 瀹炰緥` etc.), indicating a file encoding mismatch. Runtime behavior is unaffected, but maintainability and onboarding quality are reduced.
- **Evidence:** `index.js` lines 3, 12, 26, 64+.
- **Suggestion:** Normalize file encoding to UTF-8 and rewrite comments in clear Chinese/English.

## Validation notes
- `npm install --no-audit --no-fund` failed with `403 Forbidden` from registry mirror in this environment, so build-level validation could not be completed here.
