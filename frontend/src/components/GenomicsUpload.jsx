(function () {
  function PreviewTable({ rows }) {
    if (!rows.length) {
      return <div className="empty-state">No genomic file selected.</div>;
    }

    const headers = Object.keys(rows[0] || {}).slice(0, 5);
    return (
      <div className="table-shell">
        <table>
          <thead>
            <tr>{headers.map((header) => <th key={header}>{header}</th>)}</tr>
          </thead>
          <tbody>
            {rows.slice(0, 5).map((row, index) => (
              <tr key={index}>
                {headers.map((header) => <td key={header}>{String(row[header] ?? "")}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  function GenomicsUpload({ genomics, setGenomics }) {
    async function handleFile(event) {
      const file = event.target.files[0];
      if (!file) return;
      const text = await window.AppUtils.readFileAsText(file);
      setGenomics({ source: file.name, rows: window.AppUtils.parseDelimited(text) });
    }

    function useSample() {
      setGenomics({ source: "sample genomic data", rows: window.AppUtils.sampleGenomicsRows() });
    }

    return (
      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Modality 2</p>
            <h2>Genomics Input</h2>
          </div>
          <button className="ghost-button" type="button" onClick={useSample}>Sample genomics</button>
        </div>
        <div className="upload-row">
          <label className="file-control">
            <span>Upload .csv or .txt</span>
            <input accept=".csv,.txt" type="file" onChange={handleFile} />
          </label>
          <div className="source-chip">{genomics.source || "No source selected"}</div>
        </div>
        <PreviewTable rows={genomics.rows || []} />
      </section>
    );
  }

  window.GenomicsUpload = GenomicsUpload;
})();
