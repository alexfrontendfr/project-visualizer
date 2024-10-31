let currentScale = 1;
let visualizationData = null;
let transform = { scale: 1, x: 0, y: 0 };

function updateTransform() {
  const img = document.getElementById("visualization");
  if (!img) return;
  img.style.transform = `scale(${transform.scale}) translate(${transform.x}px, ${transform.y}px)`;
}

function zoomIn() {
  transform.scale = Math.min(transform.scale + 0.1, 3);
  updateTransform();
}

function zoomOut() {
  transform.scale = Math.max(transform.scale - 0.1, 0.5);
  updateTransform();
}

function resetZoom() {
  transform = { scale: 1, x: 0, y: 0 };
  updateTransform();
}

// Add mouse wheel zoom support
document.addEventListener("DOMContentLoaded", function () {
  const visualizationContainer = document.querySelector(
    ".visualization-container"
  );
  if (visualizationContainer) {
    visualizationContainer.addEventListener("wheel", (e) => {
      e.preventDefault();
      const delta = Math.sign(e.deltaY);
      if (delta < 0) {
        zoomIn();
      } else {
        zoomOut();
      }
    });
  }
});

function showResults(data) {
  document.getElementById("results").classList.remove("hidden");

  // Update visualization
  const img = document.getElementById("visualization");
  img.src = `data:image/png;base64,${data.visualization}`;

  // Update statistics
  const statsDiv = document.getElementById("stats");
  statsDiv.innerHTML = `
        <div class="bg-blue-50 rounded-lg p-4">
            <div class="font-medium text-blue-800">Total Files</div>
            <div class="text-2xl font-bold text-blue-900">${data.stats.total_files}</div>
        </div>
        <div class="bg-green-50 rounded-lg p-4">
            <div class="font-medium text-green-800">Total Directories</div>
            <div class="text-2xl font-bold text-green-900">${data.stats.total_directories}</div>
        </div>
    `;

  // Update file types with percentage bars
  const fileTypesDiv = document.getElementById("fileTypes");
  const fileTypes = Object.entries(data.stats.file_types);
  const totalFiles = data.stats.total_files;

  fileTypesDiv.innerHTML = fileTypes
    .map(([type, count]) => {
      const percentage = ((count / totalFiles) * 100).toFixed(1);
      return `
                <div class="mb-3">
                    <div class="flex justify-between text-sm mb-1">
                        <span class="font-medium">${
                          type || "no extension"
                        }</span>
                        <span>${count} files (${percentage}%)</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-500 h-2 rounded-full transition-all duration-1000" 
                             style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
    })
    .join("");
}
async function analyzeProject() {
  const path = document.getElementById("projectPath").value.trim();
  if (!path) {
    showError("Please enter a project directory path");
    return;
  }

  showLoading();
  hideError();

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: path }),
    });

    const data = await response.json();

    if (response.ok) {
      visualizationData = data;
      showResults(data);
    } else {
      showError(data.error);
    }
  } catch (error) {
    showError("An error occurred while analyzing the project.");
    console.error(error);
  } finally {
    hideLoading();
  }
}

async function exportVisualization() {
  if (!visualizationData) return;

  const format = document.getElementById("exportFormat").value;
  const button = document.querySelector(
    'button[onclick="exportVisualization()"]'
  );
  const originalText = button.textContent;

  try {
    button.disabled = true;
    button.innerHTML = '<span class="animate-spin">↻</span> Exporting...';

    const response = await fetch("/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        visualization: visualizationData.visualization,
        format: format,
      }),
    });

    if (!response.ok) throw new Error("Export failed");

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `project-structure.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (error) {
    showError("Failed to export visualization");
    console.error(error);
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
}

function showLoading() {
  document.getElementById("loading").classList.remove("hidden");
  document.getElementById("results").classList.add("hidden");
}

function hideLoading() {
  document.getElementById("loading").classList.add("hidden");
}

function showError(message) {
  const errorDiv = document.getElementById("error");
  const errorMessage = document.getElementById("errorMessage");
  errorDiv.classList.remove("hidden");
  errorMessage.textContent = message;

  // Scroll to error
  errorDiv.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hideError() {
  document.getElementById("error").classList.add("hidden");
}
