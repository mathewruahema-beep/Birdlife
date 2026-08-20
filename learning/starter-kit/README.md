# Mini Program Practice Starter Kit

A tiny but honest replica of the real ANWA architecture, for learning by doing.
Nothing here needs ANWA's appid, secrets, or client access — it runs entirely on
your machine with WeChat's free test account.

```
starter-kit/
├── miniprogram/     <- open THIS folder in WeChat DevTools
│   ├── app.json         app shell: pages, tab bar, window chrome
│   ├── app.js           startup: silent login on launch
│   ├── utils/api.js     the wx.request wrapper (token, errors, re-login)
│   └── pages/
│       ├── courses/     course catalogue (list rendering, wx:for)
│       ├── course/      detail + enrol + simulated payment + progress
│       └── me/          profile, enrolments, logout
└── mock-server/
    └── server.js    <- plays the ANWA backend. Node, zero dependencies.
```

Every concept maps 1:1 to a phase in the [Technical Runbook](../mini-program-technical-runbook.md):
the login handshake (Phase 6), the bearer-token API (Phase 5), the payment relay
with an async server notification (Phase 7), and the "server truth" rule are all
here in miniature, with comments marking what changes in the real build.

---

## Setup (once, ~15 minutes)

1. **Install WeChat DevTools** (微信开发者工具, "Stable" build) from
   https://developers.weixin.qq.com/miniprogram/en/dev/devtools/download.html
   You sign in by scanning a QR with your personal WeChat.
2. **Install Node.js** (any recent LTS) if you don't have it: https://nodejs.org
3. **Start the mock backend** in a terminal:
   ```
   cd mock-server
   node server.js
   ```
   You should see `ANWA mock API listening on http://127.0.0.1:3000`.
   Leave it running; it logs every request so you can watch the conversation.
4. **Open the app**: in DevTools choose *Import Project*, select the
   `miniprogram/` folder, and pick **Test Account (测试号)** when asked for an
   AppID. The project is preconfigured with `urlCheck: false` so the simulator
   may call `127.0.0.1` — in a real project that host would have to be on the
   whitelisted 服务器域名 list (Runbook Phase 4.2).

You should now see a course list. If you see network errors, the mock server
isn't running — check the terminal.

---

## What to watch as it runs

Open the **Console** and **Network** panels in DevTools, then:

- **Cold start** → `app.js` runs `wx.login()`, posts the code to
  `POST /api/mp/auth/login`, stores the returned token. Find that request in the
  Network panel and look at its body — this is the Phase 6 handshake.
- **Tap a course** → `GET /api/mp/courses/:id` goes out **with an
  `Authorization: Bearer …` header**. That header is the Mini Program's
  replacement for cookies.
- **Enrol in a paid course** → watch the sequence: create order → "pay"
  (simulated payment sheet) → the UI says *processing* → ~3 seconds later the
  enrolment appears. The delay is deliberate: the mock server only marks the
  order paid via a simulated **async payment notification**, and the app learns
  it by re-asking the server — never from the payment popup itself. That is the
  Phase 7 "server truth" rule, rehearsed.
- **Mark lessons complete** → `POST /api/mp/progress`, and the progress bar is
  recomputed from the server response, not from local state.

---

## Exercise ladder

Do these in order; each one is a rung. Answers aren't provided on purpose —
the mock server's logs and the DevTools Network panel are your instruments.

1. **Break it on purpose.** Stop the mock server, relaunch the app, and read the
   failure the user would see. Restart the server and use the pull-to-refresh.
   *Lesson: every screen needs a designed offline/error state.*
2. **Trace the login.** In the Network panel find the login call. What did the
   app send? What came back? Where is the token now? (Look in the *Storage*
   panel.) Then find the line in `mock-server/server.js` that fabricates the
   `openid` and read the comment above it about what the real server does
   instead (`code2session`, with the AppSecret).
3. **Feel token expiry.** In `server.js` set `TOKEN_TTL_MS` to `15000`, restart,
   use the app for 20 seconds. Watch the app hit `AUTH_EXPIRED` and silently
   re-login (the retry lives in `utils/api.js`). The user never noticed —
   that's the requirement.
4. **Change the API contract.** Add a `"level": "Beginner"` field to a course in
   `server.js`, then display it on both the list and detail pages. You have now
   done a full-stack Mini Program change.
5. **Add a page.** Create `pages/certificate/` (copy `course/` as a template),
   register it in `app.json`, and navigate to it from a completed course with
   `wx.navigateTo`. You have now touched routing.
6. **Check your package weight.** DevTools → *Details → Basic information* shows
   the bundle size. Note how small this app is against the 2 MB main-package
   cap, then look at what the real v1 must fit in the same budget.
7. **Draw the two diagrams from memory** — login and payment — then check them
   against the Runbook (Phases 6 and 7). When you can do this, you can hold the
   architecture conversation unaided.
8. **Map it to the real thing.** For each file in `miniprogram/`, say out loud
   what replaces it in the real build (e.g. `mock-server/server.js` → the BFF
   routes in `apps/web/src/app/api/mp/*` calling the existing service layer).

## What this kit deliberately fakes

| Faked here | Real mechanism | Runbook |
|---|---|---|
| Any login code accepted, openid fabricated | Server calls `code2session` with the AppSecret; `session_key` stays server-side | Phase 6 |
| Simulated payment sheet + 3s timer | `wx.requestPayment` with a signed prepay package; encrypted notify webhook | Phase 7 |
| `urlCheck: false`, localhost API | HTTPS + ICP-filed domains on the 服务器域名 whitelist (~5 edits/month) | Phase 4.2 |
| In-memory data, resets on restart | TencentDB via the one shared service layer | Phase 5 |
| No review, instant reload | 开发版 → 体验版 → Tencent review (days) → release | Phase 10 |
| No privacy declaration | Mandatory 隐私协议 before data-touching APIs work | Phase 9 |
