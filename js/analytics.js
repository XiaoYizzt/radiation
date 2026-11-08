/* Existing 51.LA page-view collector, kept from the legacy pages.
   Wrapped so that a blocked/failed third-party request cannot break the page. */
(function () {
  "use strict";
  try {
    !function (p) {
      !function (t) {
        var s = window, e = document, i = p;
        var c = "".concat("https:" === e.location.protocol ? "https://" : "http://", "sdk.51.la/js-sdk-pro.min.js");
        var n = e.createElement("script"), r = e.getElementsByTagName("script")[0];
        n.type = "text/javascript";
        n.setAttribute("charset", "UTF-8");
        n.async = !0;
        n.src = c;
        n.id = "LA_COLLECT";
        i.d = n;
        var o = function () { s.LA.ids.push(i); };
        s.LA ? (s.LA.ids && o()) : (s.LA = p, s.LA.ids = [], o());
        r.parentNode.insertBefore(n, r);
      }();
    }({ id: "JyMjQAQ8UDRTj0a4", ck: "JyMjQAQ8UDRTj0a4" });
  } catch (error) { /* analytics must never break reading */ }
})();
