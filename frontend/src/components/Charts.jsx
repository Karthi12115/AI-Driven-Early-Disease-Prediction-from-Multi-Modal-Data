(function () {
  function MiniLineChart({ data = [], valueKey = "heart_rate", label = "Heart rate trend" }) {
    const points = React.useMemo(() => {
      const values = data.map((row) => Number(row[valueKey])).filter((value) => Number.isFinite(value));
      if (!values.length) return "";
      const width = 420;
      const height = 150;
      const min = Math.min(...values);
      const max = Math.max(...values);
      const spread = max - min || 1;
      return values
        .map((value, index) => {
          const x = values.length === 1 ? width / 2 : (index / (values.length - 1)) * width;
          const y = height - ((value - min) / spread) * 118 - 16;
          return `${x.toFixed(1)},${y.toFixed(1)}`;
        })
        .join(" ");
    }, [data, valueKey]);

    if (!points) {
      return <div className="empty-state">No time-series data available.</div>;
    }

    return (
      <figure className="line-chart" aria-label={label}>
        <svg viewBox="0 0 420 150" role="img">
          <line x1="0" y1="134" x2="420" y2="134" className="chart-axis" />
          <line x1="0" y1="16" x2="0" y2="134" className="chart-axis" />
          <polyline points={points} className="chart-line" />
        </svg>
      </figure>
    );
  }

  function BarChart({ items = [], compact = false }) {
    if (!items.length) {
      return <div className="empty-state">No chart data yet.</div>;
    }

    return (
      <div className={compact ? "bar-chart compact" : "bar-chart"}>
        {items.map((item) => (
          <div className="bar-row" key={item.label}>
            <div className="bar-label">{item.label}</div>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: window.AppUtils.toPercent(item.value) }} />
            </div>
            <div className="bar-value">{window.AppUtils.toPercent(item.value)}</div>
          </div>
        ))}
      </div>
    );
  }

  function RiskGauge({ value = 0 }) {
    const radius = 52;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference * (1 - Math.max(0, Math.min(1, value)));
    return (
      <div className="risk-gauge">
        <svg viewBox="0 0 132 132" aria-label="Probability score">
          <circle cx="66" cy="66" r={radius} className="gauge-bg" />
          <circle
            cx="66"
            cy="66"
            r={radius}
            className="gauge-value"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <strong>{window.AppUtils.toPercent(value)}</strong>
      </div>
    );
  }

  function ImageHeatmap({ preview, heatmap }) {
    if (!preview) {
      return <div className="empty-state">Upload an image to preview the heatmap.</div>;
    }

    const hotspots = heatmap && heatmap.enabled ? heatmap.hotspots || [] : [];
    return (
      <div className="heatmap-frame">
        <img src={preview} alt="Medical preview with heatmap" />
        {hotspots.map((spot, index) => (
          <span
            className="heatmap-spot"
            key={`${spot.x}-${spot.y}-${index}`}
            style={{
              left: `${spot.x}%`,
              top: `${spot.y}%`,
              opacity: 0.35 + spot.strength * 0.55,
              transform: `translate(-50%, -50%) scale(${0.8 + spot.strength})`,
            }}
          />
        ))}
      </div>
    );
  }

  window.MiniLineChart = MiniLineChart;
  window.BarChart = BarChart;
  window.RiskGauge = RiskGauge;
  window.ImageHeatmap = ImageHeatmap;
})();

