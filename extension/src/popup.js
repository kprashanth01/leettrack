const titleElement = document.querySelector("#problem-title");
const detailElement = document.querySelector("#problem-detail");
const metaElement = document.querySelector("#problem-meta");
const slugElement = document.querySelector("#problem-slug");
const openInAppAction = document.querySelector("#open-in-app-action");

let detectedProblem = null;

function renderProblem(problem) {
  if (!problem?.isProblemPage) {
    detectedProblem = null;
    titleElement.textContent = "No LeetCode problem detected";
    detailElement.textContent =
      "Open a page like leetcode.com/problems/two-sum and try again.";
    metaElement.hidden = true;
    openInAppAction.hidden = true;
    return;
  }

  detectedProblem = problem;
  titleElement.textContent = problem.title || problem.slug;
  detailElement.textContent =
    "LeetTrack detected this problem from the active LeetCode tab.";
  slugElement.textContent = problem.slug;
  metaElement.hidden = false;
  openInAppAction.hidden = false;
}

function renderError() {
  detectedProblem = null;
  titleElement.textContent = "Could not inspect this tab";
  detailElement.textContent =
    "Refresh the LeetCode problem page, then open the extension again.";
  metaElement.hidden = true;
  openInAppAction.hidden = true;
}

openInAppAction.addEventListener("click", () => {
  if (!detectedProblem) {
    return;
  }

  const url = globalThis.LeetTrackUrl.buildLeetTrackProblemUrl({
    problem: detectedProblem,
  });
  chrome.tabs.create({ url });
});

chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
  if (!tab?.id || !tab.url?.includes("leetcode.com/problems/")) {
    renderProblem(null);
    return;
  }

  chrome.tabs.sendMessage(
    tab.id,
    { type: "LEETTRACK_GET_PROBLEM" },
    (response) => {
      if (chrome.runtime.lastError || response?.type !== "LEETTRACK_PROBLEM_RESULT") {
        renderError();
        return;
      }

      renderProblem(response.payload);
    },
  );
});
