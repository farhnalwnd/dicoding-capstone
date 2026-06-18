import pytest
from app.services.nlp import is_valid_skill, deduplicate_skills, match_cv_jd_hybrid, clean_skill_phrase

def test_clean_skill_phrase():
    assert clean_skill_phrase("- Collaborate") == "Collaborate"
    assert clean_skill_phrase("• Pytest") == "Pytest"
    assert clean_skill_phrase("* Docker ") == "Docker"

def test_is_valid_skill():
    domain_skills = {"Python", "FastAPI", "Docker", "Kubernetes", "Pytest", "REST API", "CI/CD", "NLP"}
    
    # Valid whitelisted skills
    assert is_valid_skill("Python", domain_skills) is True
    assert is_valid_skill("Pytest", domain_skills) is True
    assert is_valid_skill("FastAPI", domain_skills) is True
    
    # Noise/role titles
    assert is_valid_skill("Engineer", domain_skills) is False
    assert is_valid_skill("Backend Developer", domain_skills) is False
    assert is_valid_skill("frontend engineers", domain_skills) is False
    
    # Generic action verbs
    assert is_valid_skill("Collaborate", domain_skills) is False
    assert is_valid_skill("implement", domain_skills) is False
    assert is_valid_skill("building", domain_skills) is False
    assert is_valid_skill("maintaining robust", domain_skills) is False
    assert is_valid_skill("integrate Vue", domain_skills) is False
    
    # Generic nouns / adjectives
    assert is_valid_skill("Key", domain_skills) is False
    assert is_valid_skill("principles", domain_skills) is False
    assert is_valid_skill("interface", domain_skills) is False
    assert is_valid_skill("testable", domain_skills) is False

def test_user_requested_cases():
    domain_skill_set = {"REST API", "Kubernetes", "Pytest", "NLP"}
    
    # Valid cases
    valid_inputs = [
        "REST API",
        "Kubernetes",
        "Pytest",
        "NLP"
    ]
    for inp in valid_inputs:
        assert is_valid_skill(inp, domain_skill_set) is True
        
    # Invalid cases
    invalid_inputs = [
        "Key Engineer",
        "- Collaborate with frontend engineers",
        "Build testable integrations",
        "Key",
        "Engineer",
        "Collaborate",
        "frontend engineers",
        "testable",
        "integrations"
    ]
    for inp in invalid_inputs:
        assert is_valid_skill(inp, domain_skill_set) is False

def test_deduplicate_skills():
    domain_skills = ["REST API", "CI/CD", "NLP"]
    
    # Test REST vs REST API
    skills = ["REST API", "REST"]
    deduped = deduplicate_skills(skills, domain_skills)
    assert "REST API" in deduped
    assert "REST" not in deduped
    
    # Test CI vs CI/CD
    skills = ["CI", "CI/CD"]
    deduped = deduplicate_skills(skills, domain_skills)
    assert "CI/CD" in deduped
    assert "CI" not in deduped

    # Test Java vs JavaScript (should NOT deduplicate)
    skills = ["Java", "JavaScript"]
    deduped = deduplicate_skills(skills, domain_skills)
    assert "Java" in deduped
    assert "JavaScript" in deduped

    # Test NLP models vs NLP (should keep whitelisted NLP)
    skills = ["NLP", "NLP models"]
    deduped = deduplicate_skills(skills, domain_skills)
    assert "NLP" in deduped
    assert "NLP models" not in deduped

def test_match_cv_jd_hybrid_clean(monkeypatch):
    import torch
    
    # Mock model.encode to avoid loading weights or throwing AttributeError
    def mock_encode(sentences, *args, **kwargs):
        dimension = 384
        if isinstance(sentences, str):
            return torch.zeros(dimension)
        else:
            return torch.zeros(len(sentences), dimension)
            
    monkeypatch.setattr("app.services.nlp.model.encode", mock_encode)

    # Simulate JD with some skills and noisy text
    jd_text = """
    We are looking for a Backend Developer.
    Requirements:
    - Python and FastAPI
    - Experience in REST API and Docker
    - Knowledge of Kubernetes and CI/CD
    - Experience with Pytest and Git
    - Experience with MongoDB
    - Collaborate with cross-functional teams
    - Key responsibilities: building and maintaining robust backend integrations
    - Implement testable principles
    """
    
    cv_text = """
    Software Engineer with Python, FastAPI, Docker, Kubernetes, CI/CD, Pytest, Git, and MongoDB skills.
    I build APIs using REST API standards.
    """
    
    matched, missing, _ = match_cv_jd_hybrid(cv_text, jd_text, "it")
    
    # Verify expected valid skills are present
    expected_skills = {"Python", "FastAPI", "REST API", "Docker", "Kubernetes", "CI/CD", "Pytest", "Git", "MongoDB"}
    
    # The actual matched/missing lists should contain our whitelisted IT skills
    for skill in expected_skills:
        assert skill in matched or skill in missing
        
    # None of the noise words should be present in matched or missing
    noise_words = {"Engineer", "Collaborate", "Key", "building", "implement", "principles", "Backend Developer", "maintaining robust"}
    for noise in noise_words:
        assert noise not in matched
        assert noise not in missing

def test_normalization_matching(monkeypatch):
    import torch
    
    # Mock model.encode to avoid loading weights or throwing AttributeError
    def mock_encode(sentences, *args, **kwargs):
        dimension = 384
        if isinstance(sentences, str):
            return torch.zeros(dimension)
        else:
            return torch.zeros(len(sentences), dimension)
            
    monkeypatch.setattr("app.services.nlp.model.encode", mock_encode)

    jd_text = "We need experience in REST, RESTful API, RESTful APIs, CI, and NLP models, Setup, Title, Practical, Familiarity."
    cv_text = "Experienced in REST API, CI/CD, and NLP."
    
    matched, missing, _ = match_cv_jd_hybrid(cv_text, jd_text, "it")
    
    # Check that they normalized to the whitelisted terms
    assert "REST API" in matched
    assert "CI/CD" in matched
    assert "NLP" in matched
    
    # None of the unnormalized forms or general noise should leak
    unnormalized_forms = {"REST", "RESTful API", "RESTful APIs", "CI", "NLP models", "models", "Practical", "Familiarity", "Setup", "Title", "solid"}
    for item in unnormalized_forms:
        assert item not in matched
        assert item not in missing
