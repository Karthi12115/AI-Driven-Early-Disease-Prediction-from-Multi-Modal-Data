(function () {
  function ImageUpload({ medicalImage, setMedicalImage, reportImage, setReportImage }) {
    async function handleImage(event, setter, current) {
      const file = event.target.files[0];
      if (!file) return;
      const previewUrl = await window.AppUtils.fileToPreview(file);
      setter({
        ...current,
        hasImage: true,
        name: file.name,
        type: file.type,
        size: file.size,
        previewUrl,
      });
    }

    return (
      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Modality 4</p>
            <h2>Medical Images / Reports</h2>
          </div>
          <span className="status-pill">Preview enabled</span>
        </div>
        <div className="image-grid">
          <div>
            <label className="file-control">
              <span>X-ray / scan image</span>
              <input accept="image/*" type="file" onChange={(event) => handleImage(event, setMedicalImage, medicalImage)} />
            </label>
            <div className="image-preview">
              {medicalImage.previewUrl ? <img src={medicalImage.previewUrl} alt="Uploaded scan preview" /> : <span>No scan selected</span>}
            </div>
          </div>
          <div>
            <label className="file-control">
              <span>Blood report image</span>
              <input accept="image/*" type="file" onChange={(event) => handleImage(event, setReportImage, reportImage)} />
            </label>
            <div className="image-preview">
              {reportImage.previewUrl ? <img src={reportImage.previewUrl} alt="Uploaded report preview" /> : <span>No report selected</span>}
            </div>
          </div>
        </div>
        <label className="full-label">
          <span>Optional report findings text</span>
          <textarea
            rows="3"
            placeholder="Example: mild cardiomegaly, abnormal glucose, lower-zone opacity"
            value={medicalImage.findings || ""}
            onChange={(event) => setMedicalImage({ ...medicalImage, findings: event.target.value })}
          />
        </label>
      </section>
    );
  }

  window.ImageUpload = ImageUpload;
})();

