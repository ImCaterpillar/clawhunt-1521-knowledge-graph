# 设置与运行

零第三方依赖，无需安装任何包。

## 环境要求

- Python 3.8+（标准库：json / os / re / sys）

## 快速验证

```bash
# 在项目根目录
python run_tests.py        # 验收断言，期望 PASS 11 / FAIL 0
python demo.py             # 图谱演示，期望退出码 0
```

## 在自己的代码中使用

```python
from knowledge_graph import KnowledgeGraph

g = KnowledgeGraph("examples")   # 自动加载实体+关系并校验

# 直接关系查询
direct = g.direct("ent-kb-02")
# -> [('ent-enterprise-01', 'part_of', ['prj-1517-arch'])]

# 按关系类型过滤
part_of = g.direct("ent-kb-02", "part_of")

# 多跳路径（BFS）
paths = g.path("ent-ops-07", "ent-method-06")

# 证据回溯
evids = g.evidence("ent-taxonomy-05")

# 新增实体/关系（自动校验，非法抛 GraphError）
g.add_entity({...})
g.add_relation({...})
```

## 常见问题

- **关系端点必须存在？** 是。`add_relation` 前确保两端实体已注册
  （`add_entity`），否则 GraphError。
- **relation 类型有哪些？** employs / uses / depends_on / implements /
  manages / references / part_of / produces / reviewed_by。
- **Windows 中文乱码？** 脚本已内置 UTF-8 重配置。