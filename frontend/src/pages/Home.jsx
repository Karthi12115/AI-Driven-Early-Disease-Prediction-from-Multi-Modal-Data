(function () {
  function Home({ setPage }) {
    return (
      <main className="page home-page">
        <section className="home-hero">
          <div className="hero-copy">
            <p className="eyebrow">UI-Based Application</p>
            <h1>AI-Driven Early Disease Prediction from Multi-Modal Data</h1>
            <p>
              This dashboard combines electronic health records, genomics, wearable sensor streams,
              and medical images or reports to estimate disease risk early and show explainable outputs.
            </p>
            <button className="primary-button" type="button" onClick={() => setPage("input")}>
              Start Prediction
            </button>
          </div>
          <div className="hero-signal" aria-hidden="true">
            <div className="signal-panel">
              <span>EHR</span>
              <strong>Vitals + history</strong>
            </div>
            <div className="signal-panel">
              <span>Genomics</span>
              <strong>Variant markers</strong>
            </div>
            <div className="signal-panel">
              <span>Wearables</span>
              <strong>Time-series trends</strong>
            </div>
            <div className="signal-panel">
              <span>Images</span>
              <strong>CNN-style findings</strong>
            </div>
          </div>
        </section>
        <section className="info-band">
          <h2>Multimodal AI in one line</h2>
          <p>
            Each data source is encoded separately, fused with attention, and converted into mortality,
            readmission, and cardiac or neuro event risk with modality-level explanations.
          </p>
        </section>
      </main>
    );
  }

  window.Home = Home;
})();

