from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from .modes import Model, Pipe, Seabed, System, get_mode_shapes


def cli(input_file_path, model_path=None):
    import tomllib
    import os

    if model_path is None:
        model_path = os.getcwd()

    f = Path(input_file_path)
    with open(f, "rb") as i:
        inputs = tomllib.load(i)

    pipe = Pipe(**inputs["Pipe"])
    model = Model(**inputs["Model"])
    seabed = Seabed(**inputs["Seabed"])
    system = System(**inputs["System"])

    plot_modes(model_path, pipe, model, seabed, system)


def plot_modes(
    model_path: str, pipe: Pipe, model: Model, seabed: Seabed, system: System
):
    modes = get_mode_shapes(model_path, model, pipe, seabed, system)
    pts = modes[1]["mode_shape"].shape[0]
    x = np.linspace(0, (pts - 1) * model.element_length, pts)

    fig_path = Path(model_path, "mode_shapes.png")

    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")

    labels = []

    for k, v in modes.items():
        d = v["direction"]
        if d == "inline":
            color = "b"
            l = "Inline"
        elif d == "cross-flow":
            color = "g"
            l = "Cross Flow"
        else:
            color = "r"
            l = "Axial"
        label = f"Mode {k} - {v['frequency']:.2f} Hz ({l})"
        labels.append(label)
        ax.plot(x, k + v["mode_shape"][:, 0] * 0.4, color=color, label=label)

    ax.set_yticks(list(modes.keys()))
    ax.set_xlabel("KP (m)")
    ax.set_ylabel("Mode")
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(
        handles[::-1], labels[::-1], title="Frequencies", loc="outside right upper"
    )
    plt.title("Mode Shapes")
    plt.savefig(fig_path)


if __name__ == "__main__":
    import sys

    input_file = sys.argv[1]

    cli(input_file)
