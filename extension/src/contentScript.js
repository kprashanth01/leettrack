(function initLeetTrackContentScript() {
  function findHeadingText() {
    const candidates = [
      "[data-cy='question-title']",
      "div.text-title-large",
      "a[href^='/problems/']",
      "h1",
    ];

    for (const selector of candidates) {
      const element = document.querySelector(selector);
      const text = element?.textContent?.trim();
      if (text) {
        return text;
      }
    }

    return "";
  }

  function readProblemInfo() {
    return globalThis.LeetTrackProblemPage.detectLeetCodeProblem({
      href: window.location.href,
      title: document.title,
      headingText: findHeadingText(),
    });
  }

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message?.type !== "LEETTRACK_GET_PROBLEM") {
      return false;
    }

    sendResponse({
      type: "LEETTRACK_PROBLEM_RESULT",
      payload: readProblemInfo(),
    });
    return true;
  });
})();
