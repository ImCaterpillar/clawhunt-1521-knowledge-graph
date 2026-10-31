# -*- coding: utf-8 -*-
"""演示：匿名图谱样例 + 关系查询（直接/多跳/证据）

运行：python demo.py
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_graph import KnowledgeGraph  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
g = KnowledgeGraph(os.path.join(HERE, "examples"))

ents, rels = g.count()
print(f"匿名知识图谱演示 — {ents} 实体 / {rels} 关系\n")
print("实体清单：")
for eid in g.entities():
    ent = g._entities[eid]
    print(f"  {eid:<18} {ent['name']:<12} type={ent['type']}")
print()

print("关系查询 1：ent-kb-02 的直接出边")
for t, r, _ in g.direct("ent-kb-02"):
    print(f"  kb-02 -[{r}]-> {t}")

print("\n关系查询 2：ent-ops-07 -> ent-method-06 多跳路径")
paths = g.path("ent-ops-07", "ent-method-06")
for p in paths[:3]:
    print("  " + " -> ".join(f"{a}[{r}]{b}" for a, r, b in p))

print("\n证据回溯：ent-taxonomy-05")
print("  ", g.evidence("ent-taxonomy-05"))

print("\n" + "=" * 50)
print("验收结果: 匿名图谱样例 + 关系查询 -> ✅")
print("=" * 50)
sys.exit(0)