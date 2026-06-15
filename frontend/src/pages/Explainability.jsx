(function () {
  function Explainability({ prediction, setPage }) {
    if (!prediction) {
      return (
        <main className="page">
          <div className="empty-state large">
            No explanation yet.
            <button className="primary-button" type="button" onClick={() => setPage("input")}>Go to Data Input</button>
          </div>
        </main>
      );
    }

    const modalityItems = Object.entries(prediction.modalityImportance || {}).map(([label, value]) => ({ label, value }));
    const featureItems = (prediction.featureImportance || []).map((item) => ({ label: item.feature, value: item.impact }));

    return (
      <main className="page">
        <div className="page-heading">
          <div>
            <p className="eyebrow">Explainability Page</p>
            <h1>Why the model predicted this risk</h1>
          </div>
          <div className="dominant-box">
            <span>Most influential</span>
            <strong>{prediction.dominantModality.name}</strong>
          </div>
        </div>
        <section className="explain-grid">
          <div className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">EHR Impact</p>
                <h2>Feature importance</h2>
              </div>
            </div>
            <window.BarChart items={featureItems} compact />
            <div className="explain-list">
              {(prediction.featureImportance || []).map((item) => (
                <p key={item.feature}><strong>{item.feature}</strong>: {item.direction}</p>
              ))}
            </div>
          </div>
          <div className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Fusion Attention</p>
                <h2>Modality importance</h2>
              </div>
            </div>
            <window.BarChart items={modalityItems} compact />
            <div className="pipeline-list">
              {(prediction.pipeline || []).map((step) => <span key={step}>{step}</span>)}
            </div>
          </div>
        </section>
      </main>
    );
  }

  window.Explainability = Explainability;
})();

