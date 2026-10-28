# Browser publishing procedure

Use the agent's native browser or computer-use tool. Operate the visible X interface as a user would. Do not use the X API, browser-console requests, hidden network calls, or developer credentials.

## Preflight

1. Keep the final copy in a stable local draft before opening the composer.
2. Open `https://x.com/home` in the user's controllable browser.
3. Confirm that a compose control and the intended account identity are visible.
4. If X is logged out, leave the browser on the login page and ask the user to sign in and complete any CAPTCHA or two-factor authentication. Resume after the user says login is complete.
5. If multiple X accounts are available and the intended account is unclear, ask which visible account to use before posting.

Prefer controls by accessible role, visible label, or visible text. Avoid fragile selectors tied to layout or generated CSS classes. Use page-state checks instead of fixed sleeps.

## Publish a single post

1. Open the X post composer.
2. Enter the approved news copy exactly.
3. Inspect the composer for an over-limit warning, missing text, broken URL, or disabled Post button.
4. Click `Post` once.
5. Confirm success from the resulting post, profile timeline, or post permalink and record its URL.
6. Open Reply on that post, enter the mandatory app reply exactly, and click `Reply` once.
7. Verify that the app reply appears below the news post.

## Publish a thread

Prefer X's multi-post composer when it is available:

1. Enter the first numbered post.
2. Use `Add post` for every remaining numbered post in order.
3. Recheck the sequence, numbering, text, and URLs.
4. Publish the thread once.

If the multi-post composer is unavailable, publish the first post and add every following news post as a reply to the immediately previous post. Record each confirmed permalink before continuing.

After the last numbered post is verified, reply to that final post with the mandatory app reply. The app reply is not a numbered thread post.

## Verification and recovery

- Open the main permalink and confirm the displayed text and thread order.
- Confirm the app reply is attached to the main post for a single post or the final numbered post for a thread.
- Return the main post URL after verification.
- If a click has an uncertain outcome, inspect the account profile, Replies tab, and expected conversation before trying again.
- If a partial thread exists, continue from the last verified post. Do not restart the entire thread.
- If X shows a rate limit, account restriction, CAPTCHA, or security challenge, stop at that screen and report what the user must complete. Do not attempt to bypass it.
