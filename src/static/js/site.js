// The site is static, so the appointment form composes an email in the visitor's own mail app.
(function () {
  var form = document.getElementById("appointment-form");
  if (!form) return;

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      return;
    }

    var field = function (name) {
      var el = form.elements[name];
      return el ? el.value.trim() : "";
    };
    var name = (field("firstName") + " " + field("lastName")).trim();
    var lines = [
      "Name: " + name,
      "Email: " + field("email"),
      "Phone: " + field("phone"),
      "Preferred date: " + (field("date") || "Flexible"),
      "Preferred time (Eastern): " + (field("time") || "Flexible"),
      "Estimated duration (hours): " + (field("duration") || "Unknown"),
      "Delivery method: " + field("method"),
      "Service requested: " + field("service"),
      "",
      field("notes"),
    ];
    var href =
      "mailto:sales@savitas.net" +
      "?subject=" + encodeURIComponent("Appointment request: " + (field("service") || name)) +
      "&body=" + encodeURIComponent(lines.join("\n"));

    window.location.href = href;
    var done = document.getElementById("appointment-sent");
    if (done) done.classList.remove("d-none");
  });
})();
