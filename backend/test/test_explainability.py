from app.services.explainability import (
    get_recommendation_level
)

def test_strong_match():

    assert (
        get_recommendation_level(90)
        == "Strong Match"
    )

def test_good_match():

    assert (
        get_recommendation_level(75)
        == "Good Match"
    )

def test_low_match():

    assert (
        get_recommendation_level(40)
        == "Low Match"
    )