"""
Model Validation Test
Memastikan model fine-tuned dari Kaggle data loading dengan benar.
Skip jika model file tidak tersedia (CI tanpa model).
"""
import pytest
import os

# Default fallback is the local path relative to backend/
MODEL_PATH = os.environ.get("MODEL_BI_ENCODER", "../models/bi-encoder-cv-matcher")

@pytest.mark.skipif(
    not os.path.exists(MODEL_PATH),
    reason="Model file not available locally or in CI"
)
class TestModelValidation:
    def test_model_loads(self):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_PATH)
        assert model is not None

    def test_model_produces_embeddings(self):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_PATH)
        emb = model.encode(["Test CV text"])
        assert emb.shape[1] == 384  # Expected dimension for MiniLM

    def test_model_similarity_sanity(self):
        from sentence_transformers import SentenceTransformer
        from sentence_transformers.util import cos_sim
        model = SentenceTransformer(MODEL_PATH)

        # IT CV vs IT JD harus lebih mirip daripada IT CV vs HR JD
        it_cv = "Python developer experienced in Docker and FastAPI"
        it_jd = "Looking for Python backend engineer with Docker"
        hr_jd = "HR manager needed for recruitment operations"

        embs = model.encode([it_cv, it_jd, hr_jd])
        sim_match = cos_sim(embs[0], embs[1]).item()
        sim_mismatch = cos_sim(embs[0], embs[2]).item()

        assert sim_match > sim_mismatch, \
            f"IT-IT ({sim_match:.3f}) should score higher than IT-HR ({sim_mismatch:.3f})"
