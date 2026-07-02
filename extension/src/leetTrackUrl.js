(function attachLeetTrackUrl(root) {
  const DEFAULT_LEETTRACK_APP_BASE_URL = "https://leettrack-pied.vercel.app";

  function buildLeetTrackProblemUrl({
    appBaseUrl = DEFAULT_LEETTRACK_APP_BASE_URL,
    problem,
  }) {
    if (!problem?.isProblemPage || !problem.slug) {
      throw new Error("A detected LeetCode problem is required.");
    }

    const url = new URL("/problems", appBaseUrl);
    url.searchParams.set("source", "extension");
    url.searchParams.set("problemSlug", problem.slug);
    url.searchParams.set("problemTitle", problem.title || problem.slug);
    return url.toString();
  }

  const api = { DEFAULT_LEETTRACK_APP_BASE_URL, buildLeetTrackProblemUrl };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    root.LeetTrackUrl = api;
  }
})(globalThis);
