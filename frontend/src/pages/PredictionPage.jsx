(function () {
  function PredictionPage({ prediction, setPage }) {
    return (
      <main className="page">
        <div className="page-heading">
          <div>
            <p className="eyebrow">Prediction Page</p>
            <h1>Disease Risk Output</h1>
          </div>
          <button className="ghost-button" type="button" onClick={() => setPage("input")}>Edit inputs</button>
        </div>
        <window.PredictionResult prediction={prediction} />
        {prediction ? (
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Missing Data Handling</p>
                <h2>Available modality mask</h2>
              </div>
            </div>
            <div className="chip-row">
              {Object.entries(prediction.modalityMask || {}).map(([name, available]) => (
                <span className={available ? "data-chip available" : "data-chip missing"} key={name}>
                  {name === "ehr" ? "EHR" : name.charAt(0).toUpperCase() + name.slice(1)}: {available ? "available" : "missing"}
                </span>
              ))}
            </div>
          </section>
        ) : null}
      </main>
    );
  }

  window.PredictionPage = PredictionPage;
})();

