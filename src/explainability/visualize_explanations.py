"""Plot explanation artifacts for reports and presentations."""

from __future__ import annotations

from pathlib import Path


def plot_modality_attention(attention: dict[str, float], output_path: str | Path) -> Path:
    import matplotlib.pyplot as plt

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    labels = list(attention.keys())
    values = [attention[label] for label in labels]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(labels, values, color="#2f6fed")
    ax.set_ylabel("Attention weight")
    ax.set_ylim(0, max(values + [1.0]))
    ax.set_title("Modality contribution")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output
