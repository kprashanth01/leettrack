const assert = require("node:assert/strict");
const test = require("node:test");

const { buildLeetTrackProblemUrl } = require("../src/leetTrackUrl.js");

test("builds a LeetTrack URL with detected problem context", () => {
  const url = buildLeetTrackProblemUrl({
    appBaseUrl: "http://127.0.0.1:5173",
    problem: {
      isProblemPage: true,
      slug: "find-the-safest-path-in-a-grid",
      title: "Find the Safest Path in a Grid",
      url: "https://leetcode.com/problems/find-the-safest-path-in-a-grid/",
    },
  });

  assert.equal(
    url,
    "http://127.0.0.1:5173/problems?source=extension&problemSlug=find-the-safest-path-in-a-grid&problemTitle=Find+the+Safest+Path+in+a+Grid",
  );
});

test("rejects non-problem context", () => {
  assert.throws(
    () =>
      buildLeetTrackProblemUrl({
        appBaseUrl: "http://127.0.0.1:5173",
        problem: { isProblemPage: false, slug: "", title: "", url: "" },
      }),
    /LeetCode problem/,
  );
});
