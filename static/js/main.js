/**
 * AI Smart Crop Recommendation System
 * Main JavaScript — Frontend Interaction & Chart.js Graphs
 */

"use strict";

// ── State ────────────────────────────────────────────────────────────────────
let selectedLanguage = "en";
let analysisResult = null;
let profitChart = null;
let yieldChart = null;
let roiChart = null;

// ── DOM Ready ────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initImageUpload();
  initLanguagePills();
  initFormSubmit();
  initDragDrop();
});

// ── Image Upload & Preview ────────────────────────────────────────────────────
function initImageUpload() {
  const fileInput = document.getElementById("imageInput");
  const previewBox = document.getElementById("imagePreviewBox");
  const preview = document.getElementById("imagePreview");
  const removeBtn = document.getElementById("removeImage");
  const uploadZone = document.getElementById("uploadZone");

  if (!fileInput) return;

  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) showPreview(file);
  });

  if (removeBtn) {
    removeBtn.addEventListener("click", () => {
      fileInput.value = "";
      previewBox.style.display = "none";
      uploadZone.style.display = "block";
      preview.src = "";
    });
  }
}

function showPreview(file) {
  const previewBox = document.getElementById("imagePreviewBox");
  const preview = document.getElementById("imagePreview");
  const uploadZone = document.getElementById("uploadZone");
  const reader = new FileReader();
  reader.onload = (e) => {
    preview.src = e.target.result;
    previewBox.style.display = "block";
    uploadZone.style.display = "none";
  };
  reader.readAsDataURL(file);
}

// ── Drag & Drop ────────────────────────────────────────────────────────────────
function initDragDrop() {
  const zone = document.getElementById("uploadZone");
  if (!zone) return;

  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("dragging");
  });

  zone.addEventListener("dragleave", () => zone.classList.remove("dragging"));

  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("dragging");
    const file = e.dataTransfer.files[0];
    if (file && /\.(jpg|jpeg|png|webp|bmp)$/i.test(file.name)) {
      document.getElementById("imageInput").files = e.dataTransfer.files;
      showPreview(file);
    } else {
      showToast("⚠️ Please upload a JPG, PNG, or WebP image", "warning");
    }
  });
}

// ── Language Pills ─────────────────────────────────────────────────────────────
function initLanguagePills() {
  document.querySelectorAll(".lang-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      document.querySelectorAll(".lang-pill").forEach((p) => p.classList.remove("selected"));
      pill.classList.add("selected");
      selectedLanguage = pill.dataset.lang;
      document.getElementById("languageInput").value = selectedLanguage;
    });
  });
}

// ── Form Submit ────────────────────────────────────────────────────────────────
function initFormSubmit() {
  const form = document.getElementById("analysisForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("imageInput");
    if (!fileInput.files[0]) {
      showToast("📸 Please upload a land/soil image first", "warning");
      return;
    }

    const state = document.getElementById("stateSelect").value;
    if (!state) {
      showToast("📍 Please select your state", "warning");
      return;
    }

    await runAnalysis(form);
  });
}

async function runAnalysis(form) {
  const loadingOverlay = document.getElementById("loadingOverlay");
  loadingOverlay.classList.add("active");

  const steps = document.querySelectorAll(".loading-steps li");
  let stepIndex = 0;

  const stepInterval = setInterval(() => {
    if (stepIndex > 0) steps[stepIndex - 1].classList.replace("active", "done");
    if (stepIndex < steps.length) {
      steps[stepIndex].classList.add("active");
      stepIndex++;
    } else {
      clearInterval(stepInterval);
    }
  }, 1200);

  try {
    const formData = new FormData(form);
    formData.set("language", selectedLanguage);

    const response = await fetch("/analyze", {
      method: "POST",
      body: formData,
    });

    clearInterval(stepInterval);

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || "Server error");
    }

    const data = await response.json();
    analysisResult = data;

    loadingOverlay.classList.remove("active");

    if (data.success) {
      showToast("✅ Analysis complete! Loading results...", "success");
      setTimeout(() => {
        window.location.href = "/results";
      }, 800);
    }
  } catch (err) {
    clearInterval(stepInterval);
    loadingOverlay.classList.remove("active");
    showToast(`❌ Error: ${err.message}`, "error");
  }
}

// ── Results Page Charts ─────────────────────────────────────────────────────────
function initResultsCharts(profitData) {
  if (!profitData || profitData.length === 0) return;

  const crops = profitData.map((d) => d.crop);
  const profits = profitData.map((d) => d.profit);
  const revenues = profitData.map((d) => d.revenue);
  const costs = profitData.map((d) => d.cost);
  const yields = profitData.map((d) => d.yield_kg);
  const rois = profitData.map((d) => d.roi_percent);

  const greenPalette = [
    "#1B5E20", "#2E7D32", "#388E3C", "#43A047", "#4CAF50",
    "#66BB6A", "#81C784"
  ];
  const goldPalette = [
    "#C9A227", "#D4AF37", "#E8C547", "#F0D060", "#F5DD76"
  ];

  // ── Profit Bar Chart ──
  const profitCtx = document.getElementById("profitChart");
  if (profitCtx) {
    if (profitChart) profitChart.destroy();
    profitChart = new Chart(profitCtx, {
      type: "bar",
      data: {
        labels: crops,
        datasets: [
          {
            label: "Revenue (₹)",
            data: revenues,
            backgroundColor: "rgba(13,71,161,0.75)",
            borderColor: "#0D47A1",
            borderWidth: 1.5,
            borderRadius: 6,
          },
          {
            label: "Cost (₹)",
            data: costs,
            backgroundColor: "rgba(198,40,40,0.6)",
            borderColor: "#c62828",
            borderWidth: 1.5,
            borderRadius: 6,
          },
          {
            label: "Profit (₹)",
            data: profits,
            backgroundColor: profits.map((p, i) =>
              i === 0 ? "rgba(201,162,39,0.85)" : "rgba(27,94,32,0.75)"
            ),
            borderColor: profits.map((p, i) => (i === 0 ? "#C9A227" : "#1B5E20")),
            borderWidth: 1.5,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { font: { size: 12 } } },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ₹${ctx.raw.toLocaleString("en-IN")}`,
            },
          },
        },
        scales: {
          y: {
            ticks: {
              callback: (v) => `₹${(v / 1000).toFixed(0)}K`,
              font: { size: 11 },
            },
            grid: { color: "rgba(0,0,0,0.05)" },
          },
          x: { ticks: { font: { size: 11 } } },
        },
      },
    });
  }

  // ── Yield Chart ──
  const yieldCtx = document.getElementById("yieldChart");
  if (yieldCtx) {
    if (yieldChart) yieldChart.destroy();
    yieldChart = new Chart(yieldCtx, {
      type: "bar",
      data: {
        labels: crops,
        datasets: [
          {
            label: "Yield (kg/acre)",
            data: yields,
            backgroundColor: crops.map((_, i) => greenPalette[i % greenPalette.length]),
            borderRadius: 6,
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: { label: (ctx) => `Yield: ${ctx.raw.toLocaleString()} kg` },
          },
        },
        scales: {
          y: {
            ticks: { callback: (v) => `${v} kg`, font: { size: 11 } },
            grid: { color: "rgba(0,0,0,0.05)" },
          },
          x: { ticks: { font: { size: 11 } } },
        },
      },
    });
  }

  // ── ROI Doughnut ──
  const roiCtx = document.getElementById("roiChart");
  if (roiCtx) {
    if (roiChart) roiChart.destroy();
    roiChart = new Chart(roiCtx, {
      type: "doughnut",
      data: {
        labels: crops,
        datasets: [
          {
            data: rois.map((r) => Math.max(r, 0)),
            backgroundColor: [...greenPalette, ...goldPalette],
            borderWidth: 2,
            borderColor: "#ffffff",
            hoverOffset: 8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right", labels: { font: { size: 11 }, boxWidth: 14 } },
          tooltip: {
            callbacks: { label: (ctx) => `${ctx.label}: ${ctx.raw.toFixed(1)}% ROI` },
          },
        },
        cutout: "62%",
      },
    });
  }
}

// ── Chart Tab Switching ────────────────────────────────────────────────────────
function switchChart(tabName) {
  document.querySelectorAll(".chart-tab").forEach((t) => t.classList.remove("active"));
  document.querySelectorAll(".chart-panel").forEach((p) => p.classList.add("d-none"));

  const activeTab = document.querySelector(`.chart-tab[data-chart="${tabName}"]`);
  const activePanel = document.getElementById(`panel-${tabName}`);
  if (activeTab) activeTab.classList.add("active");
  if (activePanel) activePanel.classList.remove("d-none");
}

// ── Toast Notification ─────────────────────────────────────────────────────────
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const icons = { success: "✅", warning: "⚠️", error: "❌", info: "ℹ️" };
  const colors = {
    success: "#1b5e20",
    warning: "#7c5c00",
    error: "#b71c1c",
    info: "#0d47a1",
  };

  const toast = document.createElement("div");
  toast.className = "toast-msg";
  toast.style.background = colors[type] || colors.info;
  toast.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.4s ease";
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// ── Currency formatter ─────────────────────────────────────────────────────────
function formatINR(amount) {
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)}L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount.toFixed(0)}`;
}

// ── Animate numbers on scroll ─────────────────────────────────────────────────
function animateCounter(el, target, duration = 1500) {
  const start = 0;
  const step = target / (duration / 16);
  let current = start;
  const timer = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    el.textContent = Math.floor(current).toLocaleString("en-IN");
  }, 16);
}

// ── Print results ─────────────────────────────────────────────────────────────
function printResults() {
  window.print();
}

// ── Expose globally ────────────────────────────────────────────────────────────
window.initResultsCharts = initResultsCharts;
window.switchChart = switchChart;
window.showToast = showToast;
window.printResults = printResults;
window.animateCounter = animateCounter;
