// ANWA mock API — plays the role of the real backend (the BFF of Runbook Phase 5).
// Zero dependencies. Run with:  node server.js
//
// Everything is in-memory and resets on restart. Every request is logged so you
// can watch the app<->server conversation while you use the simulator.

const http = require("http");
const crypto = require("crypto");

const PORT = 3000;

// Exercise 3: set this to 15000 (15s) and watch the app silently re-login.
const TOKEN_TTL_MS = 10 * 60 * 1000;

// How long the fake payment provider takes to send its async notification.
// In reality this is WeChat Pay POSTing an encrypted webhook to notify_url.
const PAYMENT_NOTIFY_DELAY_MS = 3000;

const SECRET = "practice-only-secret"; // real system: signing key in the server's secret store

// ---------------------------------------------------------------------------
// "Database"
// ---------------------------------------------------------------------------
const courses = [
  {
    id: "c1",
    title: "Mandarin for Beginners",
    price: 0,
    cover: "🀄",
    blurb: "Tones, pinyin, and your first 100 words.",
    lessons: [
      { id: "c1l1", title: "The four tones" },
      { id: "c1l2", title: "Pinyin survival kit" },
      { id: "c1l3", title: "Greetings and names" },
    ],
  },
  {
    id: "c2",
    title: "Business Chinese",
    price: 19900, // fen (¥199.00) — money is integer minor-units, never floats
    cover: "💼",
    blurb: "Meetings, negotiation, and email etiquette.",
    lessons: [
      { id: "c2l1", title: "Introducing your company" },
      { id: "c2l2", title: "Negotiation phrases" },
    ],
  },
  {
    id: "c3",
    title: "HSK 4 Sprint",
    price: 29900,
    cover: "📚",
    blurb: "Structured drills for the HSK 4 exam.",
    lessons: [
      { id: "c3l1", title: "Vocabulary block 1" },
      { id: "c3l2", title: "Listening tactics" },
      { id: "c3l3", title: "Mock exam walkthrough" },
    ],
  },
  {
    id: "c4",
    title: "Chinese Calligraphy Basics",
    price: 0,
    cover: "🖌️",
    blurb: "Stroke order and your first characters.",
    lessons: [{ id: "c4l1", title: "Holding the brush" }],
  },
];

const users = new Map(); // openid -> { openid, name, enrolments:Set, progress:Set }
const orders = new Map(); // orderId -> { id, openid, courseId, amount, status }

// ---------------------------------------------------------------------------
// Token = payload.signature — the same *shape* as the real JWT sessions
// (packages/auth native-session), simplified so you can read it by eye.
// ---------------------------------------------------------------------------
function sign(data) {
  return crypto.createHmac("sha256", SECRET).update(data).digest("base64url");
}
function mintToken(openid) {
  const payload = Buffer.from(
    JSON.stringify({ openid, client: "miniprogram", exp: Date.now() + TOKEN_TTL_MS })
  ).toString("base64url");
  return `${payload}.${sign(payload)}`;
}
function verifyToken(header) {
  if (!header || !header.startsWith("Bearer ")) return null;
  const [payload, sig] = header.slice(7).split(".");
  if (!payload || sig !== sign(payload)) return null;
  const claims = JSON.parse(Buffer.from(payload, "base64url").toString());
  if (claims.exp < Date.now()) return "EXPIRED";
  return claims.openid;
}

// ---------------------------------------------------------------------------
// Response helpers — the stable error contract from Runbook Phase 5:
// every error body is { code, message } so the client can branch on `code`.
// ---------------------------------------------------------------------------
function json(res, status, body) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
  });
  res.end(JSON.stringify(body));
}
const err = (res, status, code, message) => json(res, status, { code, message });

function userView(u) {
  const enrolments = [...u.enrolments].map((cid) => {
    const c = courses.find((x) => x.id === cid);
    const done = c.lessons.filter((l) => u.progress.has(l.id)).length;
    return { courseId: cid, title: c.title, cover: c.cover, lessonCount: c.lessons.length, lessonsDone: done };
  });
  return { openid: u.openid, name: u.name, enrolments };
}

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------
const server = http.createServer((req, res) => {
  let body = "";
  req.on("data", (c) => (body += c));
  req.on("end", () => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const path = url.pathname;
    console.log(`${new Date().toISOString().slice(11, 19)}  ${req.method} ${path}`);
    let input = {};
    try { input = body ? JSON.parse(body) : {}; } catch (e) { /* ignore malformed */ }

    // ---- POST /api/mp/auth/login ------------------------------------------
    // REAL FLOW (Runbook Phase 6): the server takes the wx.login() code and
    // calls  GET api.weixin.qq.com/sns/jscode2session?appid&secret&js_code=...
    // WeChat returns { openid, session_key, unionid? }. The session_key never
    // leaves the server; the unionid is the join key to a website account.
    // HERE: no AppSecret exists, so we accept any code and fabricate a stable
    // openid from the simulator's code. Same contract, faked verification.
    if (req.method === "POST" && path === "/api/mp/auth/login") {
      if (!input.code) return err(res, 400, "BAD_REQUEST", "missing code");
      const openid = "mp_" + crypto.createHash("sha1").update("salt" + (input.deviceId || "dev")).digest("hex").slice(0, 10);
      if (!users.has(openid)) {
        users.set(openid, { openid, name: "Student " + openid.slice(-4), enrolments: new Set(), progress: new Set() });
        console.log(`           -> created user ${openid} (real flow: unionid lookup first!)`);
      }
      return json(res, 200, { token: mintToken(openid), profile: userView(users.get(openid)) });
    }

    // ---- everything below requires a valid token --------------------------
    const auth = verifyToken(req.headers["authorization"]);
    if (auth === "EXPIRED") return err(res, 401, "AUTH_EXPIRED", "token expired, login again");
    if (!auth) return err(res, 401, "AUTH_REQUIRED", "missing or invalid token");
    const user = users.get(auth);
    if (!user) return err(res, 401, "AUTH_REQUIRED", "unknown user");

    // ---- GET /api/mp/courses ----------------------------------------------
    // Lean payloads on purpose: the list omits lessons/blurb (Phase 5 rule).
    if (req.method === "GET" && path === "/api/mp/courses") {
      return json(res, 200, {
        courses: courses.map(({ id, title, price, cover }) => ({
          id, title, price, cover, enrolled: user.enrolments.has(id),
        })),
      });
    }

    // ---- GET /api/mp/courses/:id ------------------------------------------
    let m = path.match(/^\/api\/mp\/courses\/([\w-]+)$/);
    if (req.method === "GET" && m) {
      const c = courses.find((x) => x.id === m[1]);
      if (!c) return err(res, 404, "NOT_FOUND", "no such course");
      return json(res, 200, {
        ...c,
        enrolled: user.enrolments.has(c.id),
        lessons: c.lessons.map((l) => ({ ...l, done: user.progress.has(l.id) })),
      });
    }

    // ---- POST /api/mp/enrolments  { courseId } ----------------------------
    // Free course -> enrol immediately. Paid course -> create a pending order;
    // money must move before enrolment (and only the notify proves it moved).
    if (req.method === "POST" && path === "/api/mp/enrolments") {
      const c = courses.find((x) => x.id === input.courseId);
      if (!c) return err(res, 404, "NOT_FOUND", "no such course");
      if (user.enrolments.has(c.id)) return err(res, 409, "ALREADY_ENROLLED", "already enrolled");
      if (c.price === 0) {
        user.enrolments.add(c.id);
        return json(res, 200, { enrolled: true });
      }
      const order = { id: "ord_" + crypto.randomUUID().slice(0, 8), openid: user.openid, courseId: c.id, amount: c.price, status: "PENDING" };
      orders.set(order.id, order);
      return json(res, 200, { enrolled: false, orderId: order.id, amount: c.price });
    }

    // ---- POST /api/mp/orders/:id/pay --------------------------------------
    // REAL FLOW (Runbook Phase 7): server calls WeChat Pay v3
    // POST /v3/pay/transactions/jsapi with the MINI PROGRAM appid and the
    // user's MINI PROGRAM openid -> gets prepay_id -> signs the package the
    // client feeds to wx.requestPayment. Fulfilment then waits for WeChat's
    // encrypted async notify — NEVER the client's success callback.
    // HERE: we return fake sheet params and schedule a timer that plays the
    // role of the notify webhook.
    m = path.match(/^\/api\/mp\/orders\/([\w-]+)\/pay$/);
    if (req.method === "POST" && m) {
      const order = orders.get(m[1]);
      if (!order || order.openid !== user.openid) return err(res, 404, "NOT_FOUND", "no such order");
      if (order.status === "PAID") return err(res, 409, "ALREADY_PAID", "order already paid");
      setTimeout(() => {
        order.status = "PAID";
        users.get(order.openid).enrolments.add(order.courseId);
        console.log(`           -> [fake notify] order ${order.id} PAID, enrolment granted`);
      }, PAYMENT_NOTIFY_DELAY_MS);
      return json(res, 200, {
        paySheet: { timeStamp: String(Date.now()), nonceStr: "practice", package: "prepay_id=fake_" + order.id, signType: "RSA", paySign: "fake-signature" },
        orderId: order.id,
      });
    }

    // ---- GET /api/mp/orders/:id -------------------------------------------
    // The client polls this after "paying" — server truth, not client truth.
    m = path.match(/^\/api\/mp\/orders\/([\w-]+)$/);
    if (req.method === "GET" && m) {
      const order = orders.get(m[1]);
      if (!order || order.openid !== user.openid) return err(res, 404, "NOT_FOUND", "no such order");
      return json(res, 200, { id: order.id, status: order.status });
    }

    // ---- POST /api/mp/progress  { lessonId, done } ------------------------
    if (req.method === "POST" && path === "/api/mp/progress") {
      const course = courses.find((c) => c.lessons.some((l) => l.id === input.lessonId));
      if (!course) return err(res, 404, "NOT_FOUND", "no such lesson");
      if (!user.enrolments.has(course.id)) return err(res, 403, "NOT_ENROLLED", "enrol first");
      input.done ? user.progress.add(input.lessonId) : user.progress.delete(input.lessonId);
      const done = course.lessons.filter((l) => user.progress.has(l.id)).length;
      return json(res, 200, { courseId: course.id, lessonsDone: done, lessonCount: course.lessons.length });
    }

    // ---- GET /api/mp/me ----------------------------------------------------
    if (req.method === "GET" && path === "/api/mp/me") {
      return json(res, 200, userView(user));
    }

    return err(res, 404, "NOT_FOUND", `no route for ${req.method} ${path}`);
  });
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`ANWA mock API listening on http://127.0.0.1:${PORT}`);
  console.log(`Token TTL: ${TOKEN_TTL_MS / 1000}s | fake payment notify after ${PAYMENT_NOTIFY_DELAY_MS / 1000}s`);
});
