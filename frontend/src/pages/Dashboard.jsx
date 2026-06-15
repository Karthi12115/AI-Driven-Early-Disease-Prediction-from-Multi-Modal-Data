(function () {
  function Dashboard({ prediction, medicalImage, setPage }) {
    if (!prediction) {
      return (
        <main className="page">
          <div className="empty-state large">
            No dashboard data yet.
            <button className="primary-button" type="button" onClick={() => setPage("input")}>Go to Data Input</button>
          </div>
        </main>
      );
    }

    const riskItems = prediction.riskBreakdown || [];
    const modalityItems = Object.entries(prediction.modalityImportance || {}).map(([label, value]) => ({ label, value }));

    return (
      <main className="page">
        <div className="page-heading">
          <div>
            <p className="eyebrow">Visualization Dashboard</p>
            <h1>Risk and Modality Visuals</h1>
          </div>
        </div>
        <section className="dashboard-grid">
          <div className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Wearable Trends</p>
                <h2>Heart rate over time</h2>
              </div>
            </div>
            <window.MiniLineChart data={prediction.wearableTrends || []} valueKey="heart_rate" />
          </div>
          <div className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Risk Score Chart</p>
                <h2>Predicted outcomes</h2>
              </div>
            </div>
            <window.BarChart items={riskItems} />
            <div className="disease-list">
              <h3>Disease-wise risk scores</h3>
              <window.BarChart items={prediction.diseaseRisks || []} compact />
            </div>
          </div>
          <div className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Attention Weights</p>
                <h2>Modality comparison</h2>
              </div>
            </div>
            <window.BarChart items={modalityItems} />
          </div>
          <div className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Image Heatmap</p>
                <h2>Visual explanation</h2>
              </div>
            </div>
            <window.ImageHeatmap preview={medicalImage.previewUrl} heatmap={prediction.heatmap} />
          </div>
        </section>
      </main>
    );
  }

  window.Dashboard = Dashboard;
})();
