// Course catalogue. Demonstrates: fetching on show, lean list payloads,
// error states, pull-to-refresh, navigation with a query parameter.
const api = require("../../utils/api");

Page({
  data: { courses: [], error: "", loading: true },

  // onShow (not onLoad) so the list refreshes when you come back from a
  // detail page after enrolling — the list's `enrolled` flags are server truth.
  onShow() {
    this.fetch();
  },

  fetch() {
    this.setData({ loading: true, error: "" });
    api
      .request("/api/mp/courses")
      .then(({ courses }) => {
        this.setData({
          loading: false,
          courses: courses.map((c) => ({ ...c, priceLabel: api.yuan(c.price) })),
        });
      })
      .catch((e) => this.setData({ loading: false, error: e.message || "Failed to load" }));
  },

  onPullDownRefresh() {
    this.fetch();
    wx.stopPullDownRefresh();
  },

  openCourse(e) {
    // data-id on the tapped view arrives via the event's dataset.
    wx.navigateTo({ url: `/pages/course/course?id=${e.currentTarget.dataset.id}` });
  },
});
