(function attachLeetTrackUrl(root) {
  function buildLeetTrackProblemUrl({ appBaseUrl, problem }) {
    if (!problem?.isProblemPage || !problem.slug) {
      throw new Error("A detected LeetCode problem is required.");
    }

    const url = new URL("/problems", appBaseUrl);
    url.searchParams.set("source", "extension");
    url.searchParams.set("problemSlug", problem.slug);
    url.searchParams.set("problemTitle", problem.title || problem.slug);
    return url.toString();
  }

  const api = { buildLeetTrackProblemUrl };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    root.LeetTrackUrl = api;
  }
})(globalThis);
