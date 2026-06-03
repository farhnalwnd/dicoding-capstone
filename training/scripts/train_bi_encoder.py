import argparse
import os
import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses, SentenceTransformerTrainingArguments, SentenceTransformerTrainer
from torch.utils.data import DataLoader

def main():
    parser = argparse.ArgumentParser(description="Train a Bi-Encoder model on Triplet data.")
    parser.add_argument("--train_csv", type=str, required=True, help="Path to training CSV.")
    parser.add_argument("--eval_csv", type=str, default=None, help="Path to evaluation CSV.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the trained model.")
    parser.add_argument("--base_model", type=str, default="paraphrase-multilingual-MiniLM-L12-v2", help="Base model name.")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs.")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size.")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate.")
    
    args = parser.parse_args()

    # Create output directory if not exists
    os.makedirs(args.output_path, exist_ok=True)
    
    print(f"Loading base model: {args.base_model}")
    model = SentenceTransformer(args.base_model)
    
    print(f"Loading training data from: {args.train_csv}")
    if not os.path.exists(args.train_csv):
        raise FileNotFoundError(f"Train CSV not found at: {args.train_csv}")
        
    df_train = pd.read_csv(args.train_csv)
    
    # Validation of CSV headers
    required_cols = ["anchor", "positive", "negative"]
    if not all(col in df_train.columns for col in required_cols):
        raise ValueError(f"CSV must contain headers: {required_cols}")

    train_examples = [
        InputExample(texts=[str(row['anchor']), str(row['positive']), str(row['negative'])])
        for _, row in df_train.iterrows()
    ]
    
    train_loader = DataLoader(train_examples, shuffle=True, batch_size=args.batch_size)
    train_loss = losses.MultipleNegativesRankingLoss(model)
    
    print("Setting up training configurations...")
    training_args = SentenceTransformerTrainingArguments(
        output_dir=args.output_path,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.lr,
        save_strategy="epoch",
        logging_steps=10,
        fp16=True  # GPU acceleration if supported
    )
    
    trainer = SentenceTransformerTrainer(
        model=model,
        args=training_args,
        train_dataloader=train_loader,
        loss=train_loss
    )
    
    print("Starting Bi-Encoder training...")
    trainer.train()
    
    print(f"Saving fine-tuned model to: {args.output_path}")
    model.save_pretrained(args.output_path)
    print("Bi-Encoder training complete!")

if __name__ == "__main__":
    main()
