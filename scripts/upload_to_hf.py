import os
import sys
from huggingface_hub import HfApi

def upload_model():
    token = os.getenv("HF_TOKEN")
    if not token:
        print("Error: HF_TOKEN environment variable is not set.")
        print("Please set it using: export HF_TOKEN='your_token' (Linux/Mac) or $env:HF_TOKEN='your_token' (Windows)")
        sys.exit(1)

    # Use the username from the token to determine the repository path
    api = HfApi(token=token)
    user_info = api.whoami()
    username = user_info["name"]
    
    repo_id = f"{username}/bi-encoder-cv-matcher"
    local_dir = "models/bi-encoder-cv-matcher"

    if not os.path.exists(local_dir):
        print(f"Error: Local model directory '{local_dir}' does not exist.")
        sys.exit(1)

    print(f"Preparing to upload model from '{local_dir}' to Hugging Face Hub at '{repo_id}'...")

    try:
        # Create the repository if it doesn't exist
        api.create_repo(repo_id=repo_id, exist_ok=True, private=False)
        print(f"Repository '{repo_id}' is ready.")

        # Upload the folder
        print("Uploading files... This might take a few minutes depending on your connection.")
        api.upload_folder(
            folder_path=local_dir,
            repo_id=repo_id,
            commit_message="Upload fine-tuned Bi-Encoder CV Matcher model"
        )
        print(f"\n✅ Successfully uploaded model to: https://huggingface.co/{repo_id}")
        print("\nTo use this model in the CI/CD pipeline, ensure the repository name in .github/workflows/backend.yml matches this repo_id.")

    except Exception as e:
        print(f"\n❌ Error uploading model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    upload_model()
