# PDF样式文件说明

## 文件说明

`pdf-styles.css` - PDF导出专用样式文件，用于优化PDF打印输出效果。

## 功能特性

### 1. UI元素隐藏
- 隐藏页眉、页脚、侧边栏导航
- 隐藏搜索框、返回顶部按钮
- 隐藏语言切换器和主题切换按钮

### 2. 页面布局优化
- 主内容区域占满整个页面宽度
- 优化内容容器的边距和填充
- 移除最大宽度限制

### 3. 分页控制
- 一级标题前强制分页（新章节）
- 标题避免孤立在页面底部
- 段落避免被分页打断（orphans/widows控制）

### 4. 代码块优化
- 代码块避免分页打断
- 优化代码块背景色和边框
- 代码自动换行以适应页面宽度
- 打印时隐藏行号以节省空间

### 5. 表格优化
- 表格避免分页打断
- 优化表格边框和单元格样式
- 表头使用灰色背景突出显示

### 6. 图片和图表优化
- 图片避免分页打断
- 图片自动缩放以适应页面
- Mermaid图表优化显示
- SVG图表响应式缩放

### 7. 提示框优化
- Admonition容器避免分页
- 不同类型提示框使用不同颜色边框
- 优化背景色和边距

### 8. 链接处理
- 外部链接显示完整URL（可选）
- 内部链接不显示URL
- 链接文本使用下划线和蓝色

### 9. 页面设置
- 纸张尺寸：A4
- 页边距：上下20mm，左右15mm
- 字体：Times New Roman（正文），Courier New（代码）
- 字号：11pt（正文），9pt（代码）

## 使用方法

### 启用PDF导出

PDF导出功能通过环境变量控制。要生成PDF，需要：

1. 安装PDF导出插件：
```bash
pip install mkdocs-pdf-export-plugin
```

2. 设置环境变量并构建：
```bash
# Windows (CMD)
set ENABLE_PDF_EXPORT=1
mkdocs build

# Windows (PowerShell)
$env:ENABLE_PDF_EXPORT=1
mkdocs build

# Linux/Mac
export ENABLE_PDF_EXPORT=1
mkdocs build
```

3. PDF文件将生成在：`site/pdf/medical-embedded-knowledge-complete.pdf`

### 预览打印效果

在浏览器中预览打印效果：

1. 启动开发服务器：
```bash
mkdocs serve
```

2. 在浏览器中打开页面

3. 使用浏览器的打印预览功能（Ctrl+P 或 Cmd+P）

4. 选择"另存为PDF"查看效果

## 自定义样式

如需自定义PDF样式，可以编辑 `pdf-styles.css` 文件：

- 修改页面边距：编辑 `@page` 规则中的 `margin` 属性
- 修改字体大小：编辑 `body` 规则中的 `font-size` 属性
- 修改分页行为：编辑各元素的 `page-break-*` 属性
- 添加页眉页脚：编辑 `@page` 规则中的 `@top-center` 和 `@bottom-center`

## 注意事项

1. **插件依赖**：确保已安装 `mkdocs-pdf-export-plugin`
2. **构建时间**：生成完整PDF可能需要较长时间
3. **图表渲染**：Mermaid图表需要正确渲染才能导出
4. **外部链接**：外部链接会显示完整URL，可根据需要调整
5. **浏览器兼容**：不同浏览器的打印效果可能略有差异

## 故障排除

### PDF生成失败

如果PDF生成失败，检查：
- 是否安装了PDF导出插件
- 是否设置了 `ENABLE_PDF_EXPORT` 环境变量
- 是否有足够的磁盘空间
- 查看构建日志中的错误信息

### 样式不生效

如果样式不生效，检查：
- CSS文件路径是否正确
- mkdocs.yml中是否正确引用了CSS文件
- 浏览器缓存是否需要清除

### 分页问题

如果分页不理想，可以调整：
- `page-break-before`：控制元素前分页
- `page-break-after`：控制元素后分页
- `page-break-inside`：控制元素内分页
- `orphans` 和 `widows`：控制段落分页

## 相关文档

- [MkDocs PDF Export Plugin](https://github.com/zhaoterryy/mkdocs-pdf-export-plugin)
- [CSS Print Media Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/print)
- [CSS Paged Media](https://www.w3.org/TR/css-page-3/)
