const assert = require("node:assert/strict");
const test = require("node:test");

const {
  detectLeetCodeProblem,
  formatSlugTitle,
} = require("../src/problemPage.js");

test("detects a LeetCode problem from URL and document title", () => {
  const result = detectLeetCodeProblem({
    href: "https://leetcode.com/problems/two-sum/description/",
    title: "Two Sum - LeetCode",
    headingText: "",
  });

  assert.deepEqual(result, {
    isProblemPage: true,
    slug: "two-sum",
    title: "Two Sum",
    url: "https://leetcode.com/problems/two-sum/description/",
  });
});

test("uses heading text before falling back to title parsing", () => {
  const result = detectLeetCodeProblem({
    href: "https://leetcode.com/problems/valid-parentheses/",
    title: "Valid Parentheses - LeetCode",
    headingText: "20. Valid Parentheses",
  });

  assert.equal(result.title, "Valid Parentheses");
});

test("returns a non-problem result outside LeetCode problem URLs", () => {
  const result = detectLeetCodeProblem({
    href: "https://leetcode.com/problemset/",
    title: "Problems - LeetCode",
    headingText: "",
  });

  assert.deepEqual(result, {
    isProblemPage: false,
    slug: "",
    title: "",
    url: "https://leetcode.com/problemset/",
  });
});

test("formats a slug as a readable fallback title", () => {
  assert.equal(formatSlugTitle("number-of-islands"), "Number Of Islands");
});
