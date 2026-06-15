from io import BytesIO


def test_hr_cluster(monkeypatch, client):

    monkeypatch.setattr(
        "app.api.hr_endpoints.extract_text",
        lambda *args, **kwargs:
        "Python Developer"
    )

    monkeypatch.setattr(
        "app.api.hr_endpoints.cluster_documents",
        lambda *args, **kwargs:
        {
            "cluster_0": [
                "cv1.pdf"
            ]
        }
    )

    files = [
        (
            "cvs",
            (
                "cv1.pdf",
                BytesIO(b"dummy"),
                "application/pdf"
            )
        )
    ]

    response = client.post(
        "/api/hr/cluster",
        files=files,
        data={
            "num_clusters": 1
        }
    )

    assert response.status_code == 200