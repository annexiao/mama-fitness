// Random family-photo strip. Each .famstrip element carries a JSON list of photo
// URLs in data-photos; on load we shuffle and show data-count of them (default 3).
(function () {
  var strips = document.querySelectorAll(".famstrip");
  strips.forEach(function (el) {
    var photos;
    try {
      photos = JSON.parse(el.dataset.photos || "[]");
    } catch (e) {
      photos = [];
    }
    if (!photos.length) {
      el.remove();
      return;
    }
    for (var i = photos.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = photos[i];
      photos[i] = photos[j];
      photos[j] = t;
    }
    var n = Math.min(parseInt(el.dataset.count || "3", 10), photos.length);
    el.textContent = "";
    for (var k = 0; k < n; k++) {
      var img = document.createElement("img");
      img.src = photos[k]; // local /static/photos/*.jpg paths from build-time scan
      img.alt = "";
      img.loading = "lazy";
      el.appendChild(img);
    }
  });
})();
