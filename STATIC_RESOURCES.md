# 静态资源管理规范 (Static Resources Management)

## 规则总览

1. **项目本身的 CSS 和 JS 必须单独提取出来**
2. **使用到的第三方静态资源必须下载到本地使用**

---

## 静态资源目录结构

```
static/
├── css/
│   ├── bootstrap.min.css      # Bootstrap CSS (第三方，已本地化)
│   └── custom.css             # 项目自定义 CSS
├── js/
│   ├── bootstrap.bundle.min.js # Bootstrap JS (第三方，已本地化)
│   ├── echarts.min.js         # ECharts (第三方，已本地化)
│   └── app.js                 # 项目自定义 JS
└── vendors/                   # 其他第三方库目录 (可选)
```

---

## 规则详情

### 规则1：项目本身的 CSS 和 JS 必须单独提取

**要求：**
- 项目自定义样式必须放在 `static/css/custom.css`
- 项目自定义脚本必须放在 `static/js/app.js`
- 不要在 HTML 模板中直接编写 CSS 或 JS 代码
- 使用 `{{ url_for('static', filename='css/custom.css') }}` 引用

**示例：**

```html
<!-- ✅ 正确：使用本地自定义 CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}" />

<!-- ❌ 错误：在 HTML 中内联样式 -->
<style>
    .custom-style { color: red; }
</style>
```

### 规则2：第三方静态资源必须下载到本地

**要求：**
- 所有第三方库（CSS、JS、图片等）必须下载到 `static/` 目录
- 禁止直接从 CDN 加载第三方资源
- 下载时使用稳定版本号，避免使用 latest

**常见第三方资源处理：**

| 资源类型 | 来源 | 本地路径 |
|---------|------|---------|
| Bootstrap CSS | npm/CDN | `static/css/bootstrap.min.css` |
| Bootstrap JS | npm/CDN | `static/js/bootstrap.bundle.min.js` |
| ECharts | CDN | `static/js/echarts.min.js` |
| jQuery | CDN | `static/js/jquery.min.js` |
| Font Awesome | CDN | `static/css/fontawesome/` |

### 规则3：外部图片资源处理

**不需要本地化的外部资源：**
- 实时股票行情图（如新浪财经股票图片）- 因需要实时获取，不适合本地化

**必须本地化的图片资源：**
- 网站 logo、图标
- 静态背景图
- UI 装饰图片

---

## 新增第三方库的流程

### 步骤1：确定需要下载的库和版本

```bash
# 示例：下载 ECharts 5.4.3
npm pack echarts@5.4.3
```

### 步骤2：创建 vendors 目录（如需要）

```bash
mkdir -p static/vendors/echarts
```

### 步骤3：下载并放置文件

```bash
# 使用 curl 下载
curl -o static/js/echarts.min.js https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js
```

### 步骤4：更新 HTML 模板

```html
<!-- 修改前 (CDN) -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>

<!-- 修改后 (本地) -->
<script src="{{ url_for('static', filename='js/echarts.min.js') }}"></script>
```

### 步骤5：更新本文档

在下方表格中记录新增的第三方库信息。

---

## 第三方库清单

| 库名称 | 版本 | 用途 | 本地路径 | CDN原地址 | 下载日期 |
|-------|------|------|---------|----------|---------|
| Bootstrap | 5.3.x | UI框架 | `static/css/bootstrap.min.css`<br>`static/js/bootstrap.bundle.min.js` | - | 项目初始化 |
| ECharts | 5.4.3 | 图表库 | `static/js/echarts.min.js` | https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js | 2026-05-17 |

---

## 维护清单

- [x] 项目 CSS/JS 分离到 `static/` 目录
- [x] Bootstrap 库本地化
- [x] ECharts 库本地化
- [ ] 其他第三方库（如需要）

---

## 违规处理

违反以上规则的代码将：
1. **退回修改**：要求将第三方资源下载到本地
2. **增加代码审查**：必须经过代码审查才能合并

---

## 外部参考

- [Bootstrap 官方下载](https://getbootstrap.com/docs/5.3/getting-started/download/)
- [ECharts 官方下载](https://echarts.apache.org/zh/download.html)

---

*本文档版本：1.0*  
*创建日期：2026-05-17*