const $ = (selector) => document.querySelector(selector);

const defaultProfile = {
  template_filename: "template.xlsx",
  fields: {
    report_date: { sheet_name: "Daily", cell: "B2", language: "neutral", optional: false },
    project_name: { sheet_name: "Daily", cell: "B3", language: "neutral", optional: false },
    departure_time: { sheet_name: "Daily", cell: "B4", language: "neutral", optional: true },
    arrival_site_time: { sheet_name: "Daily", cell: "B5", language: "neutral", optional: true },
    work_content_chinese: { sheet_name: "Daily", cell: "B8", language: "chinese", optional: false },
    work_content_english: { sheet_name: "Daily", cell: "B9", language: "english", optional: false },
    next_day_plan_chinese: { sheet_name: "Daily", cell: "B10", language: "chinese", optional: true },
    next_day_plan_english: { sheet_name: "Daily", cell: "B11", language: "english", optional: true },
    remarks: { sheet_name: "Daily", cell: "B12", language: "neutral", optional: true }
  },
  photo_slots: [
    { sheet_name: "Daily", anchor_cell: "A14", width_px: 320, height_px: 240, accepted_photo_types: ["工作现场", "出发打卡"] }
  ]
};

if ($("#profile-json")) {
  $("#profile-json").value = JSON.stringify(defaultProfile, null, 2);
}

if ($("#template-form")) {
  $("#template-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const response = await fetch("/api/templates/upload", { method: "POST", body: new FormData(event.target) });
    $("#result").textContent = JSON.stringify(await response.json(), null, 2);
  });
}

if ($("#report-form")) {
  $("#report-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const response = await fetch("/api/reports/analyze", { method: "POST", body: new FormData(event.target) });
    const payload = await response.json();
    $("#result").textContent = JSON.stringify(payload, null, 2);
    if (payload.report_id) {
      window.location.href = `/preview/${payload.report_id}`;
    }
  });
}

if ($("#save-profile")) {
  $("#save-profile").addEventListener("click", async () => {
    const response = await fetch("/api/templates/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: $("#profile-json").value
    });
    $("#profile-result").textContent = JSON.stringify(await response.json(), null, 2);
  });
}

if ($("#generate-report")) {
  const reportId = window.location.pathname.split("/").pop();
  fetch(`/api/reports/${reportId}/preview`)
    .then((response) => response.json())
    .then((payload) => {
      $("#preview-json").value = JSON.stringify(payload.report, null, 2);
    });
  $("#generate-report").addEventListener("click", async () => {
    const response = await fetch(`/api/reports/${reportId}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ report: JSON.parse($("#preview-json").value) })
    });
    const payload = await response.json();
    $("#generate-result").textContent = JSON.stringify(payload, null, 2);
    if (payload.download_url) {
      window.location.href = payload.download_url;
    }
  });
}
