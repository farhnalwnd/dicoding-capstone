from app.services.parser import clean_text

def test_clean_text():

    text = """
    Visit https://google.com
    """

    cleaned = clean_text(text)

    assert "https://" not in cleaned