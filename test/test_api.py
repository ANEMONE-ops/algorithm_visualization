"""
API 集成测试
"""

import pytest


class TestHealthCheck:
    """健康检查"""

    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
        assert data["algorithms"] == 6


class TestAlgorithmsAPI:
    """算法 API 端点"""

    def test_list_algorithms(self, client):
        resp = client.get("/api/algorithms")
        assert resp.status_code == 200
        data = resp.json()
        assert "algorithms" in data
        algos = data["algorithms"]
        assert "bubble_sort" in algos
        assert "mst" in algos
        assert "hanoi" in algos

    def test_get_algorithm_detail(self, client):
        resp = client.get("/api/algorithms/bubble_sort")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "冒泡排序"
        assert "test_cases" in data
        assert len(data["test_cases"]) == 4

    def test_get_nonexistent_algorithm(self, client):
        resp = client.get("/api/algorithms/nonexistent")
        assert resp.status_code == 404

    def test_run_bubble_sort(self, client):
        resp = client.post("/api/algorithms/run", json={
            "algorithm_id": "bubble_sort",
            "data": {"array": [5, 3, 1, 4, 2]},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["algorithm_id"] == "bubble_sort"
        assert data["total_steps"] > 0
        assert "steps" in data
        assert "result" in data
        assert data["result"]["sorted_array"] == [1, 2, 3, 4, 5]

    def test_run_invalid_input(self, client):
        resp = client.post("/api/algorithms/run", json={
            "algorithm_id": "bubble_sort",
            "data": {"array": [1]},  # 少于 3 个元素
        })
        assert resp.status_code == 400

    def test_run_nonexistent_algorithm(self, client):
        resp = client.post("/api/algorithms/run", json={
            "algorithm_id": "no_such_algo",
            "data": {},
        })
        assert resp.status_code == 404

    def test_random_data(self, client):
        resp = client.post(
            "/api/algorithms/random-data?algorithm_id=bubble_sort",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "array" in data["data"]

    def test_validate_input_valid(self, client):
        resp = client.post(
            "/api/algorithms/validate?algorithm_id=bubble_sort",
            json={"array": [5, 4, 3]},
        )
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

    def test_validate_input_invalid(self, client):
        resp = client.post(
            "/api/algorithms/validate?algorithm_id=hanoi",
            json={"disks": 1},  # 少于最小限制
        )
        assert resp.status_code == 200
        assert resp.json()["valid"] is False

    def test_test_cases(self, client):
        resp = client.get("/api/algorithms/bubble_sort/test-cases")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["test_cases"]) == 4

    def test_run_hanoi(self, client):
        resp = client.post("/api/algorithms/run", json={
            "algorithm_id": "hanoi",
            "data": {"disks": 3},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["move_count"] == 7

    def test_run_mst(self, client):
        matrix = [
            [0, 2, 0, 6, 0],
            [2, 0, 3, 8, 5],
            [0, 3, 0, 0, 7],
            [6, 8, 0, 0, 9],
            [0, 5, 7, 9, 0],
        ]
        resp = client.post("/api/algorithms/run", json={
            "algorithm_id": "mst",
            "data": {"vertices": 5, "edges": matrix},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["result"]["mst_edges"]) == 4  # V-1

    def test_run_huffman(self, client):
        resp = client.post("/api/algorithms/run", json={
            "algorithm_id": "huffman",
            "data": {
                "chars": ["A", "B", "C", "D"],
                "freqs": [1, 2, 3, 4],
            },
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["result"]["codes"]) == 4

    def test_run_graph_coloring(self, client):
        matrix = [
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 1, 0],
        ]
        resp = client.post("/api/algorithms/run", json={
            "algorithm_id": "graph_coloring",
            "data": {"vertices": 4, "colors": 2, "edges": matrix},
        })
        assert resp.status_code == 200
        data = resp.json()


class TestKnowledgeAPI:
    """知识库 API"""

    def test_list_knowledge(self, client):
        resp = client.get("/api/knowledge/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["knowledge_items"]) == 6

    def test_get_knowledge_detail(self, client):
        resp = client.get("/api/knowledge/bubble_sort")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "冒泡排序 (Bubble Sort)"
        assert len(data["examples"]) == 3

    def test_get_nonexistent_knowledge(self, client):
        resp = client.get("/api/knowledge/unknown")
        assert resp.status_code == 404


class TestExportLogAPI:
    """日志导出 API（需要认证）"""

    def test_save_log(self, client, auth_headers):
        resp = client.post("/api/export/save-log", json={
            "algorithm_type": "bubble_sort",
            "input_data": '{"array": [5, 3, 1]}',
            "is_test_case": 0,
            "total_steps": 10,
            "execution_time_ms": 42,
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert "log_id" in resp.json()

    def test_get_logs(self, client, auth_headers):
        # 先保存一条日志
        client.post("/api/export/save-log", json={
            "algorithm_type": "mst",
            "input_data": "{}",
            "total_steps": 5,
        }, headers=auth_headers)

        resp = client.get("/api/export/logs?limit=10", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "logs" in data

    def test_save_log_unauthorized(self, client):
        resp = client.post("/api/export/save-log", json={
            "algorithm_type": "bubble_sort",
            "input_data": "{}",
            "total_steps": 5,
        })
        assert resp.status_code == 403


class TestCompareAPI:
    """算法对比 API"""

    def test_get_comparable_algorithms(self, client):
        resp = client.get("/api/compare/algorithms")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["algorithms"]) == 6

    def test_run_compare(self, client):
        resp = client.post("/api/compare/run", json={
            "algo_a": "bubble_sort",
            "algo_b": "quick_sort",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["algorithms"]) == 2


class TestPageRoutes:
    """前端页面路由"""

    def test_serve_index(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_serve_login(self, client):
        resp = client.get("/login.html")
        assert resp.status_code == 200
