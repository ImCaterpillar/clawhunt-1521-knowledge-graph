# -*- coding: utf-8 -*-
"""知识图谱子域 —— 建立实体、关系与证据引用；匿名图谱样例 + 关系查询验证。

对应 ClawHunt 任务 #1521（企业 Agent 系统 34/50｜知识图谱子域），
验收标准：**提供匿名图谱样例及关系查询验证**。

设计：
  - schema/entity.schema.json + schema/relation.schema.json（draft-07）
  - KnowledgeGraph：
      · 加载实体与关系（校验，零依赖）
      · 关系查询：direct（直接关系）、path（多跳路径）、evidence（证据回溯）
  - 匿名图谱样例：examples/ 下企业 Agent 系统系列知识域（脱敏）
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


class GraphError(Exception):
    pass


def _type_ok(value, t):
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "null":
        return value is None
    return True


def validate(instance, schema, path="$"):
    errors = []
    if "type" in schema and not _type_ok(instance, schema["type"]):
        return [f"{path}: 期望 {schema['type']} 实为 {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: 值 {instance!r} 不在允许集合 {schema['enum']}")
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: 长度 {len(instance)} < {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: 值 {instance!r} 不匹配模式 {schema['pattern']}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: 元素数 {len(instance)} < {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors += validate(item, schema["items"], f"{path}[{i}]")
    if isinstance(instance, dict):
        if "required" in schema:
            for k in schema["required"]:
                if k not in instance:
                    errors.append(f"{path}: 缺少必填字段 {k!r}")
        if schema.get("additionalProperties") is False \
                and "properties" in schema:
            for k in instance:
                if k not in schema["properties"]:
                    errors.append(f"{path}: 不允许的额外字段 {k!r}")
        if "properties" in schema:
            for k, sub in schema["properties"].items():
                if k in instance:
                    errors += validate(instance[k], sub, f"{path}.{k}")
    return errors


class KnowledgeGraph:
    def __init__(self, base_dir=None):
        here = os.path.dirname(os.path.abspath(__file__))
        self.entity_schema = json.load(open(
            os.path.join(here, "schema", "entity.schema.json"),
            encoding="utf-8"))
        self.relation_schema = json.load(open(
            os.path.join(here, "schema", "relation.schema.json"),
            encoding="utf-8"))
        self._entities = {}
        self._out = {}     # source -> [(target, relation, evidence)]
        self._in = {}      # target -> [(source, relation, evidence)]
        if base_dir:
            self.load_dir(base_dir)

    def add_entity(self, ent):
        errs = validate(ent, self.entity_schema)
        if errs:
            raise GraphError("实体校验失败: " + "; ".join(errs[:3]))
        eid = ent["entity_id"]
        if eid in self._entities:
            raise GraphError(f"重复实体: {eid}")
        self._entities[eid] = ent
        return eid

    def add_relation(self, rel):
        errs = validate(rel, self.relation_schema)
        if errs:
            raise GraphError("关系校验失败: " + "; ".join(errs[:3]))
        s, t = rel["source"], rel["target"]
        if s not in self._entities or t not in self._entities:
            raise GraphError(f"关系端点不存在: {s}->{t}")
        self._out.setdefault(s, []).append(
            (t, rel["relation"], rel.get("evidence_refs", [])))
        self._in.setdefault(t, []).append(
            (s, rel["relation"], rel.get("evidence_refs", [])))

    def load_dir(self, d):
        """加载 entities/entities.json + relationships/relationships.json"""
        if not os.path.isdir(d):
            return 0, 0
        ents = rels = 0
        ep = os.path.join(d, "entities.json")
        if os.path.isfile(ep):
            for e in json.load(open(ep, encoding="utf-8")):
                if "invalid" in str(e.get("entity_id", "")).lower():
                    continue
                self.add_entity(e)
                ents += 1
        rp = os.path.join(d, "relationships.json")
        if os.path.isfile(rp):
            for r in json.load(open(rp, encoding="utf-8")):
                if "invalid" in str(r.get("source", "")).lower():
                    continue
                self.add_relation(r)
                rels += 1
        return ents, rels

    # ── 关系查询（验收核心）──────────────────────────────────────
    def direct(self, source, relation=None):
        """查询实体的直接关系；relation 可选过滤。"""
        out = self._out.get(source, [])
        if relation:
            return [(t, r, ev) for (t, r, ev) in out if r == relation]
        return list(out)

    def path(self, start, end, max_depth=4):
        """BFS 查询 start->end 的多跳路径，返回路径列表。"""
        if start == end:
            return [[(start, "self", [])]]
        frontier = [(start, [])]
        seen = {start}
        results = []
        for _depth in range(max_depth):
            nxt = []
            for node, path in frontier:
                for (t, r, ev) in self._out.get(node, []):
                    new_path = path + [(node, r, t)]
                    if t == end:
                        results.append(new_path)
                    elif t not in seen:
                        seen.add(t)
                        nxt.append((t, new_path))
            frontier = nxt
            if results:
                break
        return results

    def evidence(self, entity_id):
        """回溯某实体的证据引用。"""
        ent = self._entities.get(entity_id)
        return ent.get("evidence_refs", []) if ent else []

    def entities(self):
        return sorted(self._entities)

    def count(self):
        """返回 (实体数, 关系总条数)"""
        return len(self._entities), sum(
            len(v) for v in self._out.values())