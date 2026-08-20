// The API layer, client side. This is the most important file in the kit:
// it is the Mini Program's replacement for "the browser handles cookies".
//
// Three responsibilities (all Runbook Phase 5/6 rules):
//   1. attach the bearer token to every request
//   2. speak the { code, message } error contract
//   3. on AUTH_EXPIRED, silently re-login and retry ONCE — the user never
//      sees a login screen for token expiry

const BASE = "http://127.0.0.1:3000"; // real build: https host on the 服务器域名 whitelist

function getToken() {
  return wx.getStorageSync("token") || "";
}

// wx.login() -> one-time code -> server exchanges it for identity -> our token.
// In the real system the server side of this calls WeChat's code2session with
// the AppSecret; here the mock server accepts any code (see server.js comments).
function login() {
  return new Promise((resolve, reject) => {
    wx.login({
      success: ({ code }) => {
        wx.request({
          url: `${BASE}/api/mp/auth/login`,
          method: "POST",
          data: { code },
          success: ({ statusCode, data }) => {
            if (statusCode !== 200) return reject(data);
            wx.setStorageSync("token", data.token); // storage, not cookies
            resolve(data.profile);
          },
          fail: reject,
        });
      },
      fail: reject,
    });
  });
}

// Generic request with auth + one silent retry on expiry.
function request(path, { method = "GET", data, _retried = false } = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE}${path}`,
      method,
      data,
      header: { Authorization: `Bearer ${getToken()}` },
      success: ({ statusCode, data: body }) => {
        if (statusCode >= 200 && statusCode < 300) return resolve(body);
        // Branch on the app-level error code, not the HTTP status alone.
        if (body && body.code === "AUTH_EXPIRED" && !_retried) {
          console.log("[api] token expired -> silent re-login (exercise 3 watches this)");
          return login()
            .then(() => request(path, { method, data, _retried: true }))
            .then(resolve, reject);
        }
        reject(body || { code: "HTTP_" + statusCode, message: "request failed" });
      },
      // fail = network-level failure (server down, DNS, not on whitelist...)
      fail: () => reject({ code: "NETWORK", message: "Cannot reach the server. Is mock-server running?" }),
    });
  });
}

// Format integer fen as a display price. Money is integer minor-units end to end.
function yuan(fen) {
  return fen === 0 ? "Free" : "¥" + (fen / 100).toFixed(2);
}

module.exports = { login, request, yuan };
