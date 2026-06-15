(function () {
  const DEFAULT_EHR = {
    age: 58,
    gender: "Male",
    bloodPressure: "142/88",
    sugarLevel: 154,
    heartRate: 92,
    medicalHistory: "Hypertension and family history of cardiac disease",
  };

  function App() {
    const [page, setPage] = React.useState("home");
    const [ehr, setEhr] = React.useState(DEFAULT_EHR);
    const [genomics, setGenomics] = React.useState({ source: "", rows: [] });
    const [wearable, setWearable] = React.useState({ source: "", simulated: false, rows: [] });
    const [medicalImage, setMedicalImage] = React.useState({ hasImage: false, findings: "" });
    const [reportImage, setReportImage] = React.useState({ hasImage: false });
    const [prediction, setPrediction] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState("");

    function inputSampleData() {
      const sample = window.AppUtils.randomSamplePatient();
      setEhr(sample.ehr);
      setGenomics(sample.genomics);
      setWearable(sample.wearable);
      setMedicalImage(sample.medicalImage);
      setReportImage(sample.reportImage);
      setPrediction(null);
      setError("");
    }

    async function runPrediction() {
      setLoading(true);
      setError("");
      const payload = {
        ehr,
        genomics,
        wearable,
        medicalImage: {
          hasImage: Boolean(medicalImage.hasImage),
          name: medicalImage.name,
          type: medicalImage.type,
          size: medicalImage.size,
          findings: medicalImage.findings,
        },
        reportImage: {
          hasImage: Boolean(reportImage.hasImage),
          name: reportImage.name,
          type: reportImage.type,
          size: reportImage.size,
          reportText: reportImage.reportText,
        },
      };

      try {
        const response = await fetch(`${window.AppUtils.DEFAULT_API_BASE}/predict`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!response.ok) {
          throw new Error(`Backend returned ${response.status}`);
        }
        const data = await response.json();
        setPrediction(data);
        setPage("prediction");
      } catch (err) {
        setError(`Prediction API is not reachable. Start the backend, then try again. (${err.message})`);
      } finally {
        setLoading(false);
      }
    }

    function renderPage() {
      if (page === "input") {
        return (
          <window.InputPage
            ehr={ehr}
            setEhr={setEhr}
            genomics={genomics}
            setGenomics={setGenomics}
            wearable={wearable}
            setWearable={setWearable}
            medicalImage={medicalImage}
            setMedicalImage={setMedicalImage}
            reportImage={reportImage}
            setReportImage={setReportImage}
            inputSampleData={inputSampleData}
            runPrediction={runPrediction}
            loading={loading}
            error={error}
          />
        );
      }
      if (page === "prediction") return <window.PredictionPage prediction={prediction} setPage={setPage} />;
      if (page === "explainability") return <window.Explainability prediction={prediction} setPage={setPage} />;
      if (page === "dashboard") return <window.Dashboard prediction={prediction} medicalImage={medicalImage} setPage={setPage} />;
      return <window.Home setPage={setPage} />;
    }

    return (
      <div className="app-shell">
        <window.Navbar page={page} setPage={setPage} hasPrediction={Boolean(prediction)} />
        {renderPage()}
      </div>
    );
  }

  window.App = App;
})();
