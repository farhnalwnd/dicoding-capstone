import argparse
import os
import pandas as pd
from sentence_transformers import CrossEncoder, InputExample
from torch.utils.data import DataLoader

def main():
    parser = argparse.ArgumentParser(description="Train a Cross-Encoder model on Labeled Pairs.")
    parser.add_argument("--train_csv", type=str, required=True, help="Path to training CSV.")
    parser.add_argument("--eval_csv", type=str, default=None, help="Path to evaluation CSV.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the trained model.")
    parser.add_argument("--base_model", type=str, default="paraphrase-multilingual-MiniLM-L12-v2", help="Base model name.")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs.")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size.")
    parser.add_argument("--warmup_steps", type=int, default=100, help="Warmup steps.")
    
    args = parser.parse_args()

    # Create output directory if not exists
    os.makedirs(args.output_path, exist_ok=True)
    
    print(f"Loading base Cross-Encoder: {args.base_model}")
    model = CrossEncoder(args.base_model, num_labels=1, max_length=512)
    
    print(f"Loading training data from: {args.train_csv}")
    if not os.path.exists(args.train_csv):
        raise FileNotFoundError(f"Train CSV not found at: {args.train_csv}")
        
    df_train = pd.read_csv(args.train_csv)
    
    # Validation of CSV headers
    required_cols = ["cv_text", "jd_text", "label"]
    if not all(col in df_train.columns for col in required_cols):
        raise ValueError(f"CSV must contain headers: {required_cols}")

    train_examples = [
        InputExample(texts=[str(row['cv_text']), str(row['jd_text'])], label=float(row['label']))
        for _, row in df_train.iterrows()
    ]
    
    train_loader = DataLoader(train_examples, shuffle=True, batch_size=args.batch_size)
    
    print("Starting Cross-Encoder training...")
    model.fit(
        train_objectives=[(train_loader, None)],
        epochs=args.epochs,
        warmup_steps=args.warmup_steps,
        output_path=args.output_path
    )
    
    print(f"Cross-Encoder training complete! Model saved to {args.output_path}")

if __name__ == "__main__":
    main()
