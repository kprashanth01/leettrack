const assert = require("node:assert/strict");
const test = require("node:test");

const {
  DEFAULT_LEETTRACK_APP_BASE_URL,
  buildLeetTrackProblemUrl,
} = require("../src/leetTrackUrl.js");

test("uses the deployed LeetTrack app by default", () => {
  const url = buildLeetTrackProblemUrl({
    problem: {
      isProblemPage: true,
      slug: "two-sum",
      title: "Two Sum",
      url: "https://leetcode.com/problems/two-sum/",
    },
  });

  assert.equal(DEFAULT_LEETTRACK_APP_BASE_URL, "https://leettrack-pied.vercel.app");
  assert.equal(
    url,
    "https://leettrack-pied.vercel.app/problems?source=extension&problemSlug=two-sum&problemTitle=Two+Sum",
  );
});

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
