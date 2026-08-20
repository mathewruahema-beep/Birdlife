// Profile tab: who the server thinks you are, and your enrolments.
// "Log out" wipes the stored token, so the next launch does a fresh handshake —
// useful for re-watching the login flow in the Network panel.
const api = require("../../utils/api");

Page({
  data: { me: null, error: "" },

  onShow() {
    api
      .request("/api/mp/me")
      .then((me) => this.setData({ me, error: "" }))
      .catch((e) => this.setData({ error: e.message || "Failed to load" }));
  },

  logout() {
    wx.removeStorageSync("token");
    wx.showToast({ title: "Token cleared", icon: "none" });
    // reLaunch restarts at the catalogue; app.js will log in again on demand
    // via the AUTH_REQUIRED/AUTH_EXPIRED path in utils/api.js.
    api.login().then(() => wx.reLaunch({ url: "/pages/courses/courses" }));
  },

  openCourse(e) {
    wx.navigateTo({ url: `/pages/course/course?id=${e.currentTarget.dataset.id}` });
  },
});
