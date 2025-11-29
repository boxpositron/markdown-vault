"""
Tests for commands API routes.
"""

from fastapi.testclient import TestClient


def test_list_commands(test_app: TestClient, api_headers: dict) -> None:
    """Test listing available commands."""
    response = test_app.get("/commands/", headers=api_headers)

    assert response.status_code == 200
    data = response.json()
    assert "commands" in data
    assert isinstance(data["commands"], list)
    assert len(data["commands"]) >= 3

    # Check built-in commands exist
    command_ids = {cmd["id"] for cmd in data["commands"]}
    assert "vault.list" in command_ids
    assert "vault.create" in command_ids
    assert "vault.search" in command_ids

    # Check command structure
    for cmd in data["commands"]:
        assert "id" in cmd
        assert "name" in cmd
        assert isinstance(cmd["id"], str)
        assert isinstance(cmd["name"], str)


def test_list_commands_no_auth(test_app: TestClient) -> None:
    """Test listing commands without authentication fails."""
    response = test_app.get("/commands/")
    assert response.status_code == 401


def test_execute_vault_list_command(test_app: TestClient, api_headers: dict) -> None:
    """Test executing vault.list command."""
    # Create some test files
    test_app.put(
        "/vault/cmd-test1.md",
        content="# Test 1",
        headers=api_headers,
    )
    test_app.put(
        "/vault/cmd-test2.md",
        content="# Test 2",
        headers=api_headers,
    )

    # Execute vault.list command
    response = test_app.post(
        "/commands/vault.list/",
        json={"params": {}},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "files" in data["result"]
    assert isinstance(data["result"]["files"], list)
    assert len(data["result"]["files"]) >= 2
    assert "cmd-test1.md" in data["result"]["files"]
    assert "cmd-test2.md" in data["result"]["files"]


def test_execute_vault_create_command(test_app: TestClient, api_headers: dict) -> None:
    """Test executing vault.create command."""
    response = test_app.post(
        "/commands/vault.create/",
        json={
            "params": {
                "path": "cmd-created.md",
                "content": "# Created by Command",
            }
        },
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"]["path"] == "cmd-created.md"
    assert data["result"]["created"] is True

    # Verify file was created
    verify_response = test_app.get("/vault/cmd-created.md", headers=api_headers)
    assert verify_response.status_code == 200
    assert "Created by Command" in verify_response.text


def test_execute_vault_create_command_no_content(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test executing vault.create command without content."""
    response = test_app.post(
        "/commands/vault.create/",
        json={"params": {"path": "cmd-empty.md"}},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["result"]["created"] is True

    # Verify empty file was created
    verify_response = test_app.get("/vault/cmd-empty.md", headers=api_headers)
    assert verify_response.status_code == 200
    assert verify_response.text == ""


def test_execute_vault_create_command_missing_path(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test executing vault.create command without path parameter."""
    response = test_app.post(
        "/commands/vault.create/",
        json={"params": {}},
        headers=api_headers,
    )

    assert response.status_code == 400
    assert "path" in response.json()["detail"].lower()


def test_execute_vault_search_command(test_app: TestClient, api_headers: dict) -> None:
    """Test executing vault.search command."""
    # Create test files
    test_app.put(
        "/vault/search-cmd1.md",
        content="# Python Tutorial\nLearn Python programming",
        headers=api_headers,
    )
    test_app.put(
        "/vault/search-cmd2.md",
        content="# JavaScript Guide\nLearn JavaScript",
        headers=api_headers,
    )

    # Search for Python
    response = test_app.post(
        "/commands/vault.search/",
        json={"params": {"query": "Python"}},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "results" in data["result"]
    assert "total" in data["result"]
    assert data["result"]["total"] >= 1

    # Check result structure
    if data["result"]["results"]:
        result = data["result"]["results"][0]
        assert "path" in result
        assert "matches" in result


def test_execute_vault_search_command_missing_query(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test executing vault.search command without query parameter."""
    response = test_app.post(
        "/commands/vault.search/",
        json={"params": {}},
        headers=api_headers,
    )

    assert response.status_code == 400
    assert "query" in response.json()["detail"].lower()


def test_execute_vault_search_command_max_results(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test executing vault.search command with max_results."""
    # Create multiple test files
    for i in range(5):
        test_app.put(
            f"/vault/search-limit-{i}.md",
            content=f"# Test {i}\ntest content",
            headers=api_headers,
        )

    # Search with max_results limit
    response = test_app.post(
        "/commands/vault.search/",
        json={"params": {"query": "test", "max_results": 2}},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["result"]["total"] == 2
    assert len(data["result"]["results"]) == 2


def test_execute_nonexistent_command(test_app: TestClient, api_headers: dict) -> None:
    """Test executing non-existent command returns 404."""
    response = test_app.post(
        "/commands/nonexistent.command/",
        json={"params": {}},
        headers=api_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_execute_command_no_auth(test_app: TestClient) -> None:
    """Test executing command without authentication fails."""
    response = test_app.post(
        "/commands/vault.list/",
        json={"params": {}},
    )
    assert response.status_code == 401


def test_execute_command_no_params(test_app: TestClient, api_headers: dict) -> None:
    """Test executing command without params in request body."""
    response = test_app.post(
        "/commands/vault.list/",
        json={},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
