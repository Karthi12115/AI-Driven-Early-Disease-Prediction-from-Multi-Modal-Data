(function () {
  function EHRForm({ ehr, setEhr }) {
    function update(field, value) {
      setEhr({ ...ehr, [field]: value });
    }

    return (
      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Modality 1</p>
            <h2>EHR Input</h2>
          </div>
          <span className="status-pill">Form fields</span>
        </div>
        <div className="form-grid">
          <label>
            <span>Age</span>
            <input min="0" max="120" type="number" value={ehr.age} onChange={(event) => update("age", event.target.value)} />
          </label>
          <label>
            <span>Gender</span>
            <select value={ehr.gender} onChange={(event) => update("gender", event.target.value)}>
              <option>Female</option>
              <option>Male</option>
              <option>Other</option>
              <option>Unknown</option>
            </select>
          </label>
          <label>
            <span>Blood pressure</span>
            <input placeholder="120/80" value={ehr.bloodPressure} onChange={(event) => update("bloodPressure", event.target.value)} />
          </label>
          <label>
            <span>Sugar level</span>
            <input min="0" type="number" value={ehr.sugarLevel} onChange={(event) => update("sugarLevel", event.target.value)} />
          </label>
          <label>
            <span>Heart rate</span>
            <input min="0" type="number" value={ehr.heartRate} onChange={(event) => update("heartRate", event.target.value)} />
          </label>
          <label className="span-2">
            <span>Medical history</span>
            <textarea
              rows="3"
              placeholder="Example: diabetes, hypertension, chest pain"
              value={ehr.medicalHistory}
              onChange={(event) => update("medicalHistory", event.target.value)}
            />
          </label>
        </div>
      </section>
    );
  }

  window.EHRForm = EHRForm;
})();

