# 开发指南 (Development Guidelines)

## 核心原则：隔离修改，影响范围最小化

### 黄金法则

> **修改功能之前不允许影响与之无关的功能**
> 
> Any modification to functionality must not affect unrelated features.

这是一条铁律，所有代码修改都必须遵循此原则。

---

## 修改前检查清单

在修改任何代码之前，必须完成以下检查：

### 1. 功能边界分析
- [ ] 明确要修改的功能范围
- [ ] 识别所有相关的调用方和使用者
- [ ] 列出可能受影响的模块

### 2. 影响范围评估
- [ ] 分析修改对其他功能的影响
- [ ] 评估对数据库结构的影响
- [ ] 评估对API接口的影响
- [ ] 评估对前端页面的影响

### 3. 隔离措施准备
- [ ] 准备单元测试用例
- [ ] 准备回归测试计划
- [ ] 制定回滚方案

---

## 修改执行规范

### 小步提交原则

1. **单一职责**：每次修改只做一件事
2. **增量修改**：将大改动拆分为小步骤
3. **及时验证**：每完成一个小改动立即测试

### 代码修改规范

```python
# ❌ 禁止：一次修改多个不相关的功能
def modify_something():
    change_feature_a()  # 功能A
    change_feature_b()  # 功能B（不相关）
    change_feature_c()  # 功能C（不相关）
    return result

# ✅ 正确：每次只修改一个功能
def modify_feature_a_only():
    change_feature_a()
    return result
```

### 函数/方法修改规范

1. **不改变函数签名**：除非绝对必要，不修改现有函数的参数和返回值
2. **向后兼容**：新增参数使用默认值，保持接口兼容
3. **避免副作用**：函数应该只做它名称所表示的事情

```python
# ❌ 禁止：在修改功能时引入不相关的新功能
def update_trade_record(record_id, data):
    # 原功能
    update_record_in_db(record_id, data)
    # 不相关的新功能（违反原则）
    send_notification_to_user(record_id)

# ✅ 正确：功能分离
def update_trade_record(record_id, data):
    update_record_in_db(record_id, data)

def notify_user_after_trade_update(record_id):
    send_notification_to_user(record_id)
```

---

## 测试要求

### 修改后必须测试的场景

1. **原功能测试**：确保原有功能未受影响
2. **边界条件测试**：测试边界情况和异常输入
3. **回归测试**：运行所有相关测试用例

### 测试优先级

| 优先级 | 测试内容 | 必须通过 |
|--------|----------|----------|
| P0 | 被修改功能的单元测试 | ✅ |
| P1 | 相关功能的集成测试 | ✅ |
| P2 | 整个系统的冒烟测试 | ✅ |
| P3 | 完整回归测试 | ✅ |

---

## 代码审查要点

### 修改者自检

- [ ] 修改是否只涉及目标功能？
- [ ] 是否引入了不必要的依赖？
- [ ] 是否有隐藏的副作用？
- [ ] 是否需要更新文档？

### 审查者检查

- [ ] 改动是否符合最小影响原则？
- [ ] 是否有更好的实现方式？
- [ ] 测试是否充分？
- [ ] 是否有潜在的回归风险？

---

## 场景示例

### 场景1：添加新字段

**需求**：在交易记录中添加一个新的备注字段

**错误做法**：
```python
# 一次修改多个表和不相关功能
ALTER TABLE trade_records ADD COLUMN new_field;
update_related_table();
modify_unrelated_function();
```

**正确做法**：
```python
# 步骤1：只修改数据库
ALTER TABLE trade_records ADD COLUMN new_field;

# 步骤2：验证交易记录基本功能正常
# - 测试添加记录
# - 测试查询记录
# - 测试修改记录
# - 测试删除记录

# 步骤3：单独添加表单字段
# 只修改表单，不涉及其他功能

# 步骤4：单独在需要的地方使用新字段
# 确保新字段的使用不影响现有功能
```

### 场景2：重构服务层

**需求**：重构 `StockService` 的数据获取方法

**错误做法**：
```python
# 同时修改多个不相关的方法
class StockService:
    def get_stock_info(self):
        # 改成新实现
        
    def search_stocks(self):  # 不相关的功能也被改了
        # 改成新实现
        
    def calculate_portfolio(self):  # 不相关的功能也被改了
        # 改成新实现
```

**正确做法**：
```python
class StockService:
    def get_stock_info(self):
        # 只修改这一个方法
        return self._new_implementation()
    
    def search_stocks(self):
        # 不修改，后续单独处理
        pass
    
    def calculate_portfolio(self):
        # 不修改，后续单独处理
        pass
```

---

## 回滚策略

当修改导致问题时：

1. **立即回滚**：如果发现影响无关功能，立即回滚代码
2. **分析根因**：确定是修改本身的问题还是测试遗漏
3. **重新规划**：制定更小粒度的修改方案
4. **重新测试**：确保回滚后所有功能正常

---

## 文档更新

每次修改必须更新相关文档：

- [ ] 更新函数/方法的docstring
- [ ] 更新README（如果涉及使用方式变化）
- [ ] 更新API文档（如果涉及接口变化）
- [ ] 添加迁移说明（如果涉及数据迁移）

---

## 违规处理

违反此原则的代码将：

1. **退回修改**：要求重新按最小影响原则修改
2. **增加测试**：必须添加足够的测试用例证明隔离性
3. **代码审查**：所有修改必须经过至少一次代码审查

---

## 总结

这条原则的核心是：**每次修改都应该像微创手术一样精准，只切除需要修改的部分，不伤害周围的健康组织。**

遵循这个原则将确保：
- ✅ 代码稳定性
- ✅ 快速定位问题
- ✅ 低风险迭代
- ✅ 团队协作效率

---

*本指南版本：1.0*  
*创建日期：2026-05-17*