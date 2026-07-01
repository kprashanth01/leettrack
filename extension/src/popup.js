const titleElement = document.querySelector("#problem-title");
const detailElement = document.querySelector("#problem-detail");
const metaElement = document.querySelector("#problem-meta");
const slugElement = document.querySelector("#problem-slug");

function renderProblem(problem) {
  if (!problem?.isProblemPage) {
    titleElement.textContent = "No LeetCode problem detected";
    detailElement.textContent =
      "Open a page like leetcode.com/problems/two-sum and try again.";
    metaElement.hidden = true;
    return;
  }

  titleElement.textContent = problem.title || problem.slug;
  detailElement.textContent =
    "LeetTrack detected this problem from the active LeetCode tab.";
  slugElement.textContent = problem.slug;
  metaElement.hidden = false;
}

function renderError() {
  titleElement.textContent = "Could not inspect this tab";
  detailElement.textContent =
    "Refresh the LeetCode problem page, then open the extension again.";
  metaElement.hidden = true;
}

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
