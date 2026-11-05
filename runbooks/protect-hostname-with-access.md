# Put Cloudflare Access in front of a hostname

| Value | This lab |
|---|---|
| Identity provider | GitHub |
| Reusable policy | Allow, include only my own identities |
| Session duration | 24 hours |

Use this before publishing an admin UI or anything that should be reachable
only by me.

## 1. Policy

In **Zero Trust > Access > Policies**, use or create a reusable policy:

- Action: **Allow**.
- Include: **Emails** (or the GitHub username), naming each allowed person.
- Optional require: login method GitHub.

Never include "login method is GitHub" on its own. That admits anyone with a
GitHub account.

## 2. Application

In **Zero Trust > Access > Applications > Add an application > Self-hosted**:

- Application domain: the hostname.
- Session duration: 24 hours, or shorter for admin UIs.
- Identity providers: only the ones you use.
- Policy: the one from step 1.

## 3. Test

1. In a private browser window, open the hostname. Expect the Access login
   page, not the app.
2. Sign in as yourself. Expect the app.
3. If you have a second GitHub account, sign in with it. Expect to be
   blocked.

## 4. Non-browser clients

Native mobile apps, DNS-over-HTTPS clients and anything calling an API
cannot complete an Access login. Check before protecting a hostname they
use. For those, use a **service token** policy, or a **Bypass** policy
limited to the specific path, or reach the service over the VPN instead.
