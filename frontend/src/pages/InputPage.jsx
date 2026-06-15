(function () {
  function InputPage({
    ehr,
    setEhr,
    genomics,
    setGenomics,
    wearable,
    setWearable,
    medicalImage,
    setMedicalImage,
    reportImage,
    setReportImage,
    inputSampleData,
    runPrediction,
    loading,
    error,
  }) {
    return (
      <main className="page">
        <div className="page-heading">
          <div>
            <p className="eyebrow">Core Page</p>
            <h1>Data Input</h1>
          </div>
          <div className="page-actions">
            <button className="ghost-button" type="button" onClick={inputSampleData}>
              Input sample data
            </button>
            <button className="primary-button" type="button" onClick={runPrediction} disabled={loading}>
              {loading ? "Running..." : "Run Prediction"}
            </button>
          </div>
        </div>
        {error ? <div className="error-banner">{error}</div> : null}
        <div className="input-stack">
          <window.EHRForm ehr={ehr} setEhr={setEhr} />
          <window.GenomicsUpload genomics={genomics} setGenomics={setGenomics} />
          <window.WearableUpload wearable={wearable} setWearable={setWearable} />
          <window.ImageUpload
            medicalImage={medicalImage}
            setMedicalImage={setMedicalImage}
            reportImage={reportImage}
            setReportImage={setReportImage}
          />
        </div>
      </main>
    );
  }

  window.InputPage = InputPage;
})();
