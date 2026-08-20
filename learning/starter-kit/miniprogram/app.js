// App startup. One job: make sure we have a session before any page needs one.
// This is the Runbook Phase 6 handshake, client side.
const api = require("./utils/api");

App({
  globalData: { profile: null },

  onLaunch() {
    // Silent login on cold start. The user sees nothing — logging in is the
    // app's problem, not theirs. api.login() runs wx.login() -> POST /auth/login
    // and stores the returned token in wx storage.
    api
      .login()
      .then((profile) => {
        this.globalData.profile = profile;
        console.log("[app] logged in as", profile.openid);
      })
      .catch((e) => console.error("[app] login failed — is the mock server running?", e));
  },
});
