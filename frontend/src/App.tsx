const foundationItems = [
  "React + Vite frontend shell",
  "FastAPI backend health endpoint",
  "Architecture and setup documentation",
];

function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Foundation milestone</p>
        <h1>LeetTrack</h1>
        <p className="summary">
          A competitive programming tracker being built step by step with clean
          architecture, thoughtful documentation, and professional Git workflow.
        </p>
      </section>

      <section className="panel" aria-labelledby="foundation-heading">
        <h2 id="foundation-heading">What exists in this milestone</h2>
        <ul>
          {foundationItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}

export default App;
