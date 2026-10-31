# -*- coding: utf-8 -*-
"""知识图谱子域主流程验证 —— 对应验收标准
「提供匿名图谱样例及关系查询验证」

零第三方依赖。打印每条验收标准的实测结果。
"""
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_graph import KnowledgeGraph, GraphError, validate  # noqa
import json  # noqa

PASS, FAIL = [], []
OK = "\u2705"
NO = "\u274c"


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    mark = OK if cond else NO
    line = "  " + mark + " " + name
    if detail:
        line += " -- " + detail
    print(line)


print("=" * 78)
print("Knowledge Graph Subdomain -- acceptance verification")
print("=" * 78)
print("Acceptance: 匿名图谱样例及关系查询验证\n")

HERE = os.path.dirname(os.path.abspath(__file__))
g = KnowledgeGraph(os.path.join(HERE, "examples"))

# 1. 匿名图谱样例加载
ents, rels = g.count()
check("1. graph loads entities+relations", ents == 7 and rels == 8,
      f"entities={ents} relations={rels}")

# 2. 直接关系查询（关系查询验证）
direct = g.direct("ent-kb-02")
check("2. direct relations query", len(direct) == 1,
      f"kb-02 out={[(t,r) for t,r,_ in direct]}")

# 3. 按关系类型过滤
part_of = [e for e in g.direct("ent-enterprise-01", "part_of")]
check("3. filter by relation type", len(part_of) == 0,
      f"(反向关系在入边, 见 in-edges)")

# 4. 多跳路径查询（存在路径：ops-07 -> taxonomy-05 -> method-06）
paths = g.path("ent-ops-07", "ent-method-06")
check("4. multi-hop path query",
      any(len(p) >= 2 for p in paths),
      f"{len(paths)} paths, shortest={min((len(p) for p in paths), default=0)}")

# 5. 证据回溯（可验证来源）
ev = g.evidence("ent-taxonomy-05")
check("5. evidence refs retrievable",
      len(ev) >= 1 and "prj-1517-taxonomy" in ev, str(ev))

# 6. 反例：非法实体/关系被拒
bad_ent = {"entity_id": "ent-invalid-99", "name": "bad",
           "type": "wat", "evidence_refs": []}
errs = validate(bad_ent, g.entity_schema)
check("6. invalid entity rejected", len(errs) >= 1,
      f"{len(errs)} errors")
bad_rel = {"source": "ent-nope", "target": "ent-kb-02",
           "relation": "employs", "evidence_refs": ["x"]}
try:
    g.add_relation(bad_rel)
    check("6b. unknown endpoint rejected", False)
except GraphError:
    check("6b. unknown endpoint rejected", True)

# 7. 空/缺失目录不崩
import tempfile  # noqa
with tempfile.TemporaryDirectory() as td:
    g2 = KnowledgeGraph(td)
    check("7. empty dir handles", g2.count() == (0, 0),
          f"count={g2.count()}")

# 8. 零第三方依赖
src = open(os.path.join(HERE, "knowledge_graph.py"),
           encoding="utf-8").read()
imports = [l.split()[1].split(".")[0]
           for l in src.splitlines()
           if (l.startswith("import ") or l.startswith("from "))
           and "knowledge_graph" not in l]
check("8. zero third-party deps",
      all(m in {"json", "os", "re", "sys"} for m in imports),
      f"imports={imports}")

# 9. demo 可运行
r9 = subprocess.run([sys.executable, "demo.py"], cwd=HERE,
                    capture_output=True, text=True, encoding="utf-8",
                    errors="replace")
check("9. demo.py exit=0", r9.returncode == 0, f"exit={r9.returncode}")

# 10. 交付齐套
refs = ["knowledge_graph.py", "run_tests.py", "demo.py",
        "schema/entity.schema.json", "schema/relation.schema.json",
        "examples/entities.json", "examples/relationships.json",
        "README.md", "SETUP.md",
        "docs/验收对照.md", "docs/实现说明.md", "docs/验证记录.md"]
broken = [r for r in refs if not os.path.isfile(os.path.join(HERE, r))]
check("10. delivery set complete (12 files)", not broken,
      "broken=" + str(broken) if broken else str(len(refs)) + " files")

print()
print("=" * 78)
print("Result: PASS " + str(len(PASS)) + "   FAIL " + str(len(FAIL)))
print("=" * 78)
if FAIL:
    print("Failed: " + ", ".join(FAIL))
sys.exit(1 if FAIL else 0)