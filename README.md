# 知识图谱子域 — 实体、关系与证据引用；匿名图谱 + 关系查询

对应 ClawHunt 任务 **#1521**（企业 Agent 系统 34/50｜知识图谱子域）。

**验收标准**：提供**匿名图谱样例及关系查询验证**。

## 一条命令验证全部

```bash
python run_tests.py      # -> PASS 11 / FAIL 0
python demo.py           # -> 匿名图谱 + 关系查询演示
```

## 验收三要素（与验收标准逐条对应）

**① 匿名图谱样例路径**
`examples/entities.json`（7 个实体：企业 Agent 系统系列项目/知识库/
角色卡/路由/分类法等）+ `examples/relationships.json`（8 条关系），
全部为脱敏的内部/合成数据，无真实客户。

**② 核心实现（图谱 + 关系查询）路径**
`knowledge_graph.py` —— `KnowledgeGraph`：
- 实体/关系两套 schema（entity/relation，draft-07，校验零依赖）
- `direct()` 直接关系查询（可按关系类型过滤）
- `path()` 多跳路径查询（BFS）
- `evidence()` 证据引用回溯（可验证来源）

**③ 关系查询验证：运行命令 + 正/反例预期输出**

```bash
python run_tests.py
# ✅ 2. direct relations query -- kb-02 out=[('ent-enterprise-01', 'part_of')]
# ✅ 4. multi-hop path query -- ops-07 -> taxonomy-05 -> method-06
# ✅ 5. evidence refs retrievable -- ['prj-1517-taxonomy']
# ✅ 6. invalid entity rejected
# Result: PASS 11   FAIL 0
```

匿名图谱 + 三种查询的可复现验证，即"匿名图谱样例 + 关系查询验证"。

## 快速开始

```bash
# 零第三方依赖（纯 Python 标准库）
python run_tests.py          # 全部验收验证
python demo.py               # 图谱 + 关系查询演示
```

## 目录

```
.
├── knowledge_graph.py       # 图谱（实体/关系/查询/证据回溯，核心）
├── run_tests.py             # 验收验证
├── demo.py                  # 匿名图谱 + 关系查询演示
├── schema/
│   ├── entity.schema.json   # 实体模板（draft-07）
│   └── relation.schema.json # 关系模板（draft-07）
├── examples/
│   ├── entities.json        # 匿名图谱样例（7 实体）
│   └── relationships.json   # 匿名图谱样例（8 关系）
├── docs/（验收对照 / 实现说明 / 验证记录）
├── SETUP.md
└── README.md
```

## 设计要点

1. **实体/关系双 schema**：级别校验 + `additionalProperties: false`，
   实体类型/关系类型均为枚举，杜绝拼写漂移。
2. **证据引用可回溯**：每个实体/关系带 `evidence_refs`，可回链来源
   资料（对应"证据引用"验收表达）。
3. **三类关系查询**：直接（direct）、多跳（path BFS）、证据回溯
   （evidence）——覆盖验收"关系查询验证"。
4. **完整性校验**：关系端点必须已存在；非法实体/未知端点被拒。
5. **匿名合规**：样例全脱敏，无真实客户/项目数据。

## 环境

- Python 3.8+
- **零第三方依赖**（纯标准库 json/os/re/sys）

## 边界说明

本单范围 = 高价值业务子域的实体/关系/证据引用建模 + 查询验证；
图谱的持久化/可视化/嵌入知识库 —— 属其他拆分单。