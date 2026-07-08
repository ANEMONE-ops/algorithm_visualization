"""
算法引擎单元测试
"""

import pytest

from algorithm_viz.algorithms.base import AlgorithmEngine, StepInfo, StepType
from algorithm_viz.algorithms.bubble_sort import BubbleSortEngine
from algorithm_viz.algorithms.quick_sort import QuickSortEngine
from algorithm_viz.algorithms.mst import MSTEngine
from algorithm_viz.algorithms.huffman import HuffmanEngine
from algorithm_viz.algorithms.hanoi import HanoiEngine
from algorithm_viz.algorithms.graph_coloring import GraphColoringEngine


# ---------------------------------------------------------------------------
# 基类测试
# ---------------------------------------------------------------------------

class TestAlgorithmEngine:
    """测试抽象基类"""

    def test_cannot_instantiate_directly(self):
        """直接调用 generate_steps 应抛出 NotImplementedError"""
        engine = AlgorithmEngine()
        with pytest.raises(NotImplementedError):
            engine.generate_steps([])

    def test_add_step(self):
        """测试添加步骤"""
        engine = AlgorithmEngine()
        engine.add_step(StepType.INIT, "测试步骤")
        assert engine.total_steps == 1
        assert engine.steps[0].description == "测试步骤"

    def test_to_dict(self):
        """测试序列化"""
        engine = AlgorithmEngine()
        engine.add_step(StepType.COMPARE, "比较", data_snapshot=[1, 2, 3])
        result = engine.to_dict()
        assert result["total_steps"] == 1
        assert len(result["steps"]) == 1

    def test_default_get_result(self):
        """默认 get_result 返回空字典"""
        engine = AlgorithmEngine()
        assert engine.get_result() == {}


# ---------------------------------------------------------------------------
# 冒泡排序
# ---------------------------------------------------------------------------

class TestBubbleSort:
    def test_basic_sort(self):
        engine = BubbleSortEngine()
        steps = engine.generate_steps([5, 3, 1, 4, 2])
        assert len(steps) > 0
        assert engine.get_result()["sorted_array"] == [1, 2, 3, 4, 5]

    def test_already_sorted(self):
        engine = BubbleSortEngine()
        steps = engine.generate_steps([1, 2, 3, 4, 5])
        result = engine.get_result()
        assert result["sorted_array"] == [1, 2, 3, 4, 5]

    def test_reverse_sorted(self):
        engine = BubbleSortEngine()
        steps = engine.generate_steps([5, 4, 3, 2, 1])
        assert engine.get_result()["sorted_array"] == [1, 2, 3, 4, 5]

    def test_validate_input_valid(self):
        valid, err = BubbleSortEngine.validate_input({"array": [3, 1, 2]})
        assert valid is True
        assert err == ""

    def test_validate_input_missing_field(self):
        valid, err = BubbleSortEngine.validate_input({})
        assert valid is False
        assert "缺少" in err

    def test_validate_input_too_small(self):
        valid, err = BubbleSortEngine.validate_input({"array": [1]})
        assert valid is False

    def test_random_data(self):
        data = BubbleSortEngine.generate_random_data()
        assert "array" in data
        assert len(data["array"]) >= 3
        assert all(isinstance(x, int) for x in data["array"])

    def test_test_cases(self):
        cases = BubbleSortEngine.get_test_cases()
        assert len(cases) == 4
        for case in cases:
            valid, _ = BubbleSortEngine.validate_input(case["data"])
            assert valid, f"Test case '{case['name']}' should be valid"

    def test_comparison_count(self):
        engine = BubbleSortEngine()
        engine.generate_steps([3, 2, 1])
        result = engine.get_result()
        assert result["comparisons"] > 0
        assert result["swaps"] > 0


# ---------------------------------------------------------------------------
# 快速排序
# ---------------------------------------------------------------------------

class TestQuickSort:
    def test_basic_sort(self):
        engine = QuickSortEngine()
        engine.generate_steps([8, 3, 9, 5, 2, 7])
        assert engine.get_result()["sorted_array"] == [2, 3, 5, 7, 8, 9]

    def test_single_element(self):
        engine = QuickSortEngine()
        engine.generate_steps([1, 2, 3])
        assert engine.get_result()["sorted_array"] == [1, 2, 3]

    def test_random_data(self):
        data = QuickSortEngine.generate_random_data()
        assert "array" in data


# ---------------------------------------------------------------------------
# Prim 最小生成树
# ---------------------------------------------------------------------------

class TestMST:
    MATRIX = [
        [0, 2, 0, 6, 0],
        [2, 0, 3, 8, 5],
        [0, 3, 0, 0, 7],
        [6, 8, 0, 0, 9],
        [0, 5, 7, 9, 0],
    ]

    def test_basic_mst(self):
        engine = MSTEngine()
        engine.generate_steps({"vertices": 5, "edges": self.MATRIX})
        result = engine.get_result()
        assert result["total_weight"] > 0
        assert len(result["mst_edges"]) == 4  # V-1 = 4

    def test_validate_asymmetric(self):
        bad_matrix = [
            [0, 1, 0],
            [2, 0, 0],
            [0, 0, 0],
        ]
        valid, err = MSTEngine.validate_input(
            {"vertices": 3, "edges": bad_matrix},
        )
        assert valid is False
        assert "不对称" in err

    def test_test_cases_valid(self):
        for case in MSTEngine.get_test_cases():
            valid, _ = MSTEngine.validate_input(case["data"])
            assert valid, f"Test case '{case['name']}' should be valid"


# ---------------------------------------------------------------------------
# 哈夫曼树
# ---------------------------------------------------------------------------

class TestHuffman:
    def test_basic_huffman(self):
        engine = HuffmanEngine()
        engine.generate_steps({
            "chars": ["A", "B", "C", "D"],
            "freqs": [1, 2, 3, 4],
        })
        result = engine.get_result()
        assert len(result["codes"]) == 4
        assert result["wpl"] > 0

    def test_validate_mismatch(self):
        valid, err = HuffmanEngine.validate_input({
            "chars": ["A", "B"],
            "freqs": [1],
        })
        assert valid is False
        assert "不匹配" in err

    def test_validate_negative_freq(self):
        valid, err = HuffmanEngine.validate_input({
            "chars": ["A", "B"],
            "freqs": [1, -1],
        })
        assert valid is False


# ---------------------------------------------------------------------------
# 汉诺塔
# ---------------------------------------------------------------------------

class TestHanoi:
    def test_2_disks(self):
        engine = HanoiEngine()
        engine.generate_steps({"disks": 2})
        result = engine.get_result()
        assert result["move_count"] == 3
        assert result["is_optimal"] is True

    def test_3_disks(self):
        engine = HanoiEngine()
        engine.generate_steps({"disks": 3})
        result = engine.get_result()
        assert result["move_count"] == 7

    def test_validate_too_few(self):
        valid, _ = HanoiEngine.validate_input({"disks": 1})
        assert valid is False

    def test_validate_too_many(self):
        valid, _ = HanoiEngine.validate_input({"disks": 20})
        assert valid is False


# ---------------------------------------------------------------------------
# 图着色
# ---------------------------------------------------------------------------

class TestGraphColoring:
    BIPARTITE = [
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0],
    ]

    def test_bipartite_2color(self):
        engine = GraphColoringEngine()
        engine.generate_steps({
            "vertices": 4, "colors": 2, "edges": self.BIPARTITE,
        })
        result = engine.get_result()
        assert result["solutions_count"] >= 1

    def test_triangle_2color_impossible(self):
        """K3 不能用 2 种颜色着色"""
        k3 = [
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0],
        ]
        engine = GraphColoringEngine()
        engine.generate_steps({
            "vertices": 3, "colors": 2, "edges": k3,
        })
        result = engine.get_result()
        assert result["solutions_count"] == 0

    def test_validate_non_binary(self):
        bad_matrix = [
            [0, 2, 0],
            [2, 0, 0],
            [0, 0, 0],
        ]
        valid, err = GraphColoringEngine.validate_input({
            "vertices": 3, "colors": 3, "edges": bad_matrix,
        })
        assert valid is False
