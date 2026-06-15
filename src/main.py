"""CLI for training, inference, and evaluation."""

from __future__ import annotations

import argparse
import json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multimodal healthcare prediction system")
    parser.add_argument("--mode", choices=["train", "infer", "evaluate"], required=True)
    parser.add_argument("--demo", action="store_true", help="Run synthetic demo path")
    parser.add_argument("--checkpoint", default="artifacts/models/demo_model.pt")
    parser.add_argument("--predictions")
    parser.add_argument("--labels")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        if args.mode == "train":
            if not args.demo:
                raise SystemExit("Only --demo training is wired until a real dataset adapter is configured.")
            from src.train import train_demo

            path = train_demo(output_path=args.checkpoint)
            print(f"Saved demo model to {path}")
        elif args.mode == "infer":
            if not args.demo:
                raise SystemExit("Provide --demo or integrate a patient input adapter.")
            from src.infer import infer_demo

            result = infer_demo(args.checkpoint)
            print(json.dumps(result, indent=2))
        elif args.mode == "evaluate":
            if not args.predictions or not args.labels:
                raise SystemExit("--predictions and --labels are required for evaluation.")
            from src.evaluate import evaluate_prediction_files

            metrics = evaluate_prediction_files(args.predictions, args.labels)
            print(json.dumps(metrics, indent=2))
    except ModuleNotFoundError as error:
        if error.name == "torch":
            raise SystemExit("PyTorch is required for train/infer. Run `pip install -r requirements.txt`.") from error
        raise


if __name__ == "__main__":
    main()
