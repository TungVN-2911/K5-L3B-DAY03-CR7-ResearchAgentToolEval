"""Offline checks for the team's CP4 dataset; these do not measure a model."""
import inspect
import json
from pathlib import Path

from tools import TOOL_FUNCTIONS, load_tool_declarations


ROOT = Path(__file__).resolve().parents[1]


def test_group_eval_meets_cp4_contract() -> None:
    dataset = json.loads((ROOT / "data/eval_group.json").read_text(encoding="utf-8"))
    cases = dataset["cases"]
    declarations = {tool["name"]: tool for tool in load_tool_declarations(ROOT / "artifacts/tools.yaml")}
    assert len(cases) == len({case["id"] for case in cases}) == 10
    assert sum("query" in case for case in cases) == 5
    assert sum("turns" in case for case in cases) == 5

    supplied_inputs = set()
    for name in ("eval_base.json", "eval_research_extension.json"):
        supplied = json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
        for case in supplied["cases"]:
            supplied_inputs.add(json.dumps(case.get("query", case.get("turns")), sort_keys=True))

    expected_tools = set()
    for case in cases:
        assert case["phase"] == "B" and case["suite"] == "group"
        assert case["failure_type"] in dataset["allowed_failure_types"]
        assert case["metadata"]["what_it_tests"].strip()
        assert ("query" in case) != ("turns" in case)
        if "query" in case:
            assert case["query"].strip()
        else:
            assert len(case["turns"]) >= 3
            assert case["turns"][-1]["role"] == "user"
            assert all(turn["role"] in {"user", "assistant"} and turn["content"].strip() for turn in case["turns"])
        assert json.dumps(case.get("query", case.get("turns")), sort_keys=True) not in supplied_inputs
        expect = case["expect"]
        assert bool(expect.get("no_tool")) != bool(expect.get("tool_calls"))
        for call in expect.get("tool_calls", []):
            name, args = call["name"], call["args"]
            assert name in declarations and name in TOOL_FUNCTIONS
            assert set(args) <= set(declarations[name]["parameters"]["properties"])
            inspect.signature(TOOL_FUNCTIONS[name]).bind(**args)
            expected_tools.add(name)
    assert "source_audit" in expected_tools
