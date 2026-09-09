"""Train the small Verizon support intent model and print a quick summary."""
from __future__ import annotations

from src.intent_classifier import train_model


def main():
    bundle = train_model()
    print("Model trained successfully")
    print(f"Labels: {bundle['labels']}")
    print(f"Training rows: {len(bundle['train'][0])}")


if __name__ == "__main__":
    main()
