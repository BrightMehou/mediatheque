# from collections.abc import Generator

# import pytest
# from fastapi.testclient import TestClient


# def test_topic_crud(client: TestClient):
#     """Teste le cycle complet de vie d'un topic."""
#     # CREATE
#     response = client.post(
#         "/topic/",
#         json={"topic": "Python"},
#     )

#     assert response.status_code == 201

#     data = response.json()
#     assert "id" in data

#     topic_id = data["id"]

#     # GET ALL
#     response = client.get("/topic/")

#     assert response.status_code == 200

#     topics = response.json()

#     assert any(
#         topic["id"] == topic_id and topic["topic"] == "Python"
#         for topic in topics
#     )

#     # UPDATE
#     response = client.put(
#         f"/topic/{topic_id}",
#         json={"topic": "Python Backend"},
#     )

#     assert response.status_code == 204

#     # Vérifie la modification via GET ALL
#     response = client.get("/topic/")

#     assert response.status_code == 200

#     topics = response.json()

#     assert any(
#         topic["id"] == topic_id and topic["topic"] == "Python Backend"
#         for topic in topics
#     )

#     # DELETE
#     response = client.delete(f"/topic/{topic_id}")

#     assert response.status_code == 204

#     # Vérifie que le topic a bien été supprimé
#     response = client.get("/topic/")

#     assert response.status_code == 200

#     topics = response.json()

#     assert not any(topic["id"] == topic_id for topic in topics)
