import type { RevisionItem } from "../../types/dashboard";

type RevisionPreviewProps = {
  items: RevisionItem[];
};

function RevisionPreview({ items }: RevisionPreviewProps) {
  return (
    <section className="dashboard-section" aria-labelledby="revision-preview-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Revision queue</p>
          <h2 id="revision-preview-heading">Notes to revisit</h2>
        </div>
      </div>

      <div className="revision-list">
        {items.map((item) => (
          <article className="revision-item" key={item.id}>
            <div>
              <h3>{item.title}</h3>
              <p>{item.note}</p>
            </div>
            <span>{item.dueLabel}</span>
          </article>
        ))}
      </div>
    </section>
  );
}

export default RevisionPreview;
