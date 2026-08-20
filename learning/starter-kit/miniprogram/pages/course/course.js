// Course detail: enrol (free), buy (paid, simulated payment), lesson progress.
// This page rehearses the two Runbook flows that matter most:
//   - Phase 7 payment relay, including the "server truth" rule
//   - progress writes where the UI reflects the server's answer, not local state
const api = require("../../utils/api");

Page({
  data: { course: null, error: "", paying: false },

  onLoad(query) {
    this.id = query.id; // from /pages/course/course?id=c2
  },
  onShow() {
    this.fetch();
  },

  fetch() {
    api
      .request(`/api/mp/courses/${this.id}`)
      .then((course) => {
        const done = course.lessons.filter((l) => l.done).length;
        this.setData({
          course: { ...course, priceLabel: api.yuan(course.price), done },
          error: "",
        });
        wx.setNavigationBarTitle({ title: course.title });
      })
      .catch((e) => this.setData({ error: e.message || "Failed to load" }));
  },

  enrol() {
    api
      .request("/api/mp/enrolments", { method: "POST", data: { courseId: this.id } })
      .then((r) => {
        if (r.enrolled) {
          wx.showToast({ title: "Enrolled", icon: "success" });
          return this.fetch();
        }
        // Paid course: server created a PENDING order — go pay for it.
        this.pay(r.orderId);
      })
      .catch((e) => wx.showToast({ title: e.message || "Failed", icon: "none" }));
  },

  pay(orderId) {
    this.setData({ paying: true });
    api
      .request(`/api/mp/orders/${orderId}/pay`, { method: "POST" })
      .then(({ paySheet }) => {
        // REAL BUILD: wx.requestPayment(paySheet) opens WeChat's payment sheet.
        // The test appid cannot open a real sheet, so we show a stand-in dialog.
        // Either way the next step is identical: the success callback is NOT
        // proof of payment — only the server's verified notify is. So we poll.
        wx.showModal({
          title: "WeChat Pay (simulated)",
          content: `package: ${paySheet.package}\n\nIn the real app this is wx.requestPayment().`,
          confirmText: "Pay",
          cancelText: "Cancel",
          success: ({ confirm }) => {
            if (!confirm) return this.setData({ paying: false });
            this.waitForServerTruth(orderId, 10);
          },
        });
      })
      .catch((e) => {
        this.setData({ paying: false });
        wx.showToast({ title: e.message || "Payment failed", icon: "none" });
      });
  },

  // Poll the order until the server says PAID (the mock notify lands ~3s later).
  // The real app does the same after wx.requestPayment resolves.
  waitForServerTruth(orderId, attemptsLeft) {
    if (attemptsLeft === 0) {
      this.setData({ paying: false });
      return wx.showToast({ title: "Still processing — pull to refresh", icon: "none" });
    }
    api.request(`/api/mp/orders/${orderId}`).then(({ status }) => {
      if (status === "PAID") {
        this.setData({ paying: false });
        wx.showToast({ title: "Payment confirmed", icon: "success" });
        return this.fetch(); // enrolment now exists server-side
      }
      setTimeout(() => this.waitForServerTruth(orderId, attemptsLeft - 1), 1000);
    });
  },

  toggleLesson(e) {
    const { lessonId, done } = e.currentTarget.dataset;
    api
      .request("/api/mp/progress", {
        method: "POST",
        data: { lessonId, done: !done },
      })
      .then(() => this.fetch()) // re-render from server truth
      .catch((e2) => wx.showToast({ title: e2.message || "Failed", icon: "none" }));
  },
});
