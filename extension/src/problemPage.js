(function attachProblemPage(root) {
  function getProblemSlug(href) {
    try {
      const url = new URL(href);
      const segments = url.pathname.split("/").filter(Boolean);
      const problemsIndex = segments.indexOf("problems");

      if (problemsIndex === -1) {
        return "";
      }

      return segments[problemsIndex + 1] || "";
    } catch {
      return "";
    }
  }

  function formatSlugTitle(slug) {
    return slug
      .split("-")
      .filter(Boolean)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  }

  function cleanTitle(value) {
    return value
      .replace(/\s*-\s*LeetCode\s*$/i, "")
      .replace(/^\d+\.\s*/, "")
      .trim();
  }

  function detectLeetCodeProblem({ href, title, headingText }) {
    const slug = getProblemSlug(href);
    const fallbackUrl = typeof href === "string" ? href : "";

    if (!slug) {
      return {
        isProblemPage: false,
        slug: "",
        title: "",
        url: fallbackUrl,
      };
    }

    const detectedTitle =
      cleanTitle(headingText || "") ||
      cleanTitle(title || "") ||
      formatSlugTitle(slug);

    return {
      isProblemPage: true,
      slug,
      title: detectedTitle,
      url: fallbackUrl,
    };
  }

  const api = {
    detectLeetCodeProblem,
    formatSlugTitle,
    getProblemSlug,
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    root.LeetTrackProblemPage = api;
  }
})(globalThis);
