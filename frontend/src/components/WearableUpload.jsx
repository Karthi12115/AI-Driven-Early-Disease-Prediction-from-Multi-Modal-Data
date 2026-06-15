(function () {
  function WearableUpload({ wearable, setWearable }) {
    async function handleFile(event) {
      const file = event.target.files[0];
      if (!file) return;
      const text = await window.AppUtils.readFileAsText(file);
      setWearable({ source: file.name, simulated: false, rows: window.AppUtils.parseDelimited(text) });
    }

    function simulate() {
      setWearable({ source: "real-time simulation", simulated: true, rows: window.AppUtils.simulateWearableRows() });
    }

    return (
      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Modality 3</p>
            <h2>Wearable Sensor Input</h2>
          </div>
          <button className="ghost-button" type="button" onClick={simulate}>Simulate data</button>
        </div>
        <div className="upload-row">
          <label className="file-control">
            <span>Upload time-series .csv</span>
            <input accept=".csv,.txt" type="file" onChange={handleFile} />
          </label>
          <div className="source-chip">{wearable.source || "No wearable stream selected"}</div>
        </div>
        <window.MiniLineChart data={wearable.rows || []} valueKey="heart_rate" label="Heart rate over time" />
      </section>
    );
  }

  window.WearableUpload = WearableUpload;
})();

