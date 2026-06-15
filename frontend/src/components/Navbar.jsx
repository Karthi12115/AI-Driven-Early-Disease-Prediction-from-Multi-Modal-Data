(function () {
  function Navbar({ page, setPage, hasPrediction }) {
    const items = [
      ["home", "Home"],
      ["input", "Data Input"],
      ["prediction", "Prediction"],
      ["explainability", "Explainability"],
      ["dashboard", "Dashboard"],
    ];

    return (
      <header className="topbar">
        <button className="brand" onClick={() => setPage("home")} type="button">
          <span className="brand-mark">AI</span>
          <span>
            <strong>Early Disease Prediction</strong>
            <small>Multimodal clinical dashboard</small>
          </span>
        </button>
        <nav className="nav-tabs" aria-label="Main pages">
          {items.map(([id, label]) => (
            <button
              key={id}
              className={page === id ? "active" : ""}
              disabled={!hasPrediction && (id === "prediction" || id === "explainability" || id === "dashboard")}
              onClick={() => setPage(id)}
              type="button"
            >
              {label}
            </button>
          ))}
        </nav>
      </header>
    );
  }

  window.Navbar = Navbar;
})();

