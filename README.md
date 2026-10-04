# Two-Factor Login (Flask + Vanilla JS)

A lightweight two-step authentication flow: email/password login followed by a
time-limited verification code, built with Flask on the backend and plain
JavaScript on the frontend (no frameworks, no third-party auth libraries).

## How It Works

1. **Step 1 — Credentials**
   User submits email and password. JavaScript intercepts the form submit and
   sends the data to `/login` via `fetch()`. Flask verifies the credentials
   against the stored password hash (`werkzeug.security.check_password_hash`)
   and, on success, stores a pending user id in the session.

2. **Step 2 — Verification Code**
   On a successful response, the login form is hidden and replaced with a
   code input, a submit button, and a live 60-second countdown. The code
   (sent separately, e.g. via email) is submitted to `/verify-code` via
   `fetch()`.

3. **Timeout**
   If the countdown reaches zero before the code is submitted, the user is
   redirected back to `/login` and must restart the flow.

4. **Result**
   - Correct code → session is finalized, user is redirected to the homepage.
   - Incorrect code → an inline "Wrong code" message is shown in red, no
     page reload.

## Tech Stack

- **Backend:** Flask, Flask sessions, `werkzeug.security` for password hashing
- **Frontend:** Vanilla JavaScript (`fetch` API), no frameworks
- **Styling:** CSS custom properties (`var(--color-primary)`, etc.) for easy
  theming

## Key Implementation Details

- All API communication uses JSON (`Content-Type: application/json`),
  so Flask routes read input with `request.get_json()` rather than
  `request.form`.
- The authenticated user's id is **never** trusted from the client during
  verification — it's tracked server-side via `session['pending_user_id']`
  to prevent spoofing.
- Password verification uses `check_password_hash(stored_hash, plain_password)`
  — passwords are only ever hashed at account-creation time, never during
  login.
- Routes hit via `fetch()` return JSON (`jsonify(...)`), not
  `redirect(...)`, since `fetch` does not trigger a browser navigation on
  redirect responses. Client-side redirects are handled explicitly with
  `window.location.href`.

## Project Structure

```
/templates
  index.html      # authenticated landing page
  login.html      # login + 2FA verification UI
/static
  (styles inlined per-page via CSS variables)
app.py            # Flask routes: /login, /verify-code, /
```

## Routes

| Route          | Method | Purpose                                   | Returns                          |
|----------------|--------|--------------------------------------------|-----------------------------------|
| `/login`       | POST   | Verify email/password                     | `{"success": bool, "id": int}`   |
| `/verify-code` | POST   | Verify the time-limited code               | `{"success": bool}`              |
| `/`            | GET    | Authenticated homepage                     | Rendered HTML                    |

## Setup

1. Install dependencies:
   ```bash
   pip install flask werkzeug
   ```
2. Set a Flask secret key (required for sessions):
   ```python
   app.secret_key = "your-secret-key-here"
   ```
3. Run the app:
   ```bash
   flask run
   ```

## Notes

This is a demo/portfolio implementation intended to illustrate the two-step
login pattern. In production, consider:
- Rate-limiting login and verification attempts
- Expiring verification codes server-side (not just via the client-side
  countdown)
- Using HTTPS-only, `HttpOnly`, `Secure` session cookies
