(function () {
  function PredictionResult({ prediction }) {
    if (!prediction) {
      return <div className="empty-state">Run prediction to view disease risk.</div>;
    }

    const levelClass = String(prediction.riskLevel || "Low").toLowerCase();
    return (
      <section className="result-layout">
        <div className={`risk-card ${levelClass}`}>
          <p className="eyebrow">Disease Risk</p>
          <h2>{prediction.riskLevel}</h2>
          <window.RiskGauge value={prediction.probability} />
          <p>Probability score: <strong>{Number(prediction.probability).toFixed(2)}</strong></p>
        </div>
        <div className="panel flat">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Predicted Outcome</p>
              <h2>Clinical risk heads</h2>
            </div>
          </div>
          {prediction.predictedDisease ? (
            <div className="disease-card">
              <div>
                <span>Predicted disease risk</span>
                <strong>{prediction.predictedDisease.name}</strong>
              </div>
              <div className="disease-score">
                {window.AppUtils.toPercent(prediction.predictedDisease.probability)}
              </div>
              <p>
                Evidence: {(prediction.predictedDisease.supportingEvidence || []).join(", ")}
              </p>
            </div>
          ) : null}
          <window.BarChart items={prediction.riskBreakdown || []} />
          {prediction.diseaseRisks ? (
            <div className="disease-list">
              <h3>Disease-wise risk scores</h3>
              <window.BarChart items={prediction.diseaseRisks || []} compact />
            </div>
          ) : null}
        </div>
      </section>
    );
  }

  window.PredictionResult = PredictionResult;
})();
