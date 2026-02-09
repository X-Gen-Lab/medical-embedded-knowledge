# 自定义JavaScript说明
# Custom JavaScript Documentation

## 文件列表 (File List)

### search-handler.js

自定义搜索结果处理脚本，实现搜索无结果时的友好提示和建议。

Custom search results handler that implements friendly prompts and suggestions when no search results are found.

#### 功能特性 (Features)

1. **搜索无结果处理** (No Results Handling)
   - 自动检测搜索无结果情况
   - 显示友好的提示消息
   - Automatically detects no search results
   - Displays friendly prompt messages

2. **搜索建议** (Search Suggestions)
   - 检查拼写提示
   - 使用通用关键词建议
   - 同义词搜索建议
   - 中英文切换建议
   - Spelling check tips
   - Generic keyword suggestions
   - Synonym search suggestions
   - Chinese-English switch suggestions

3. **热门搜索词** (Popular Searches)
   - 显示常用搜索词列表
   - 提供快速访问链接
   - Displays frequently searched terms
   - Provides quick access links

4. **分类浏览** (Category Browsing)
   - 提供主要分类链接
   - 帮助用户快速定位内容
   - Provides main category links
   - Helps users quickly locate content

#### 实现原理 (Implementation)

使用 `MutationObserver` 监听搜索结果容器的DOM变化，当检测到无结果时，动态插入自定义内容。

Uses `MutationObserver` to monitor DOM changes in the search results container, and dynamically inserts custom content when no results are detected.

#### 配置说明 (Configuration)

可以通过修改以下变量来自定义内容：

You can customize the content by modifying the following variables:

```javascript
// 热门搜索词列表
const popularSearches = [
    { term: 'RTOS', url: '/technical-knowledge/rtos/' },
    // 添加更多...
];

// 分类浏览链接
const categoryLinks = [
    { name: '核心技术知识', url: '/technical-knowledge/' },
    // 添加更多...
];
```

#### 需求追溯 (Requirements Traceability)

- **需求 6.2**: 搜索无结果处理
- **Requirement 6.2**: No search results handling

## 使用方法 (Usage)

这些JavaScript文件会自动通过 `mkdocs.yml` 中的 `extra_javascript` 配置加载：

These JavaScript files are automatically loaded through the `extra_javascript` configuration in `mkdocs.yml`:

```yaml
extra_javascript:
  - javascripts/search-handler.js
```

## 浏览器兼容性 (Browser Compatibility)

- Chrome/Edge: ✓
- Firefox: ✓
- Safari: ✓
- IE11: ✗ (不支持 MutationObserver / MutationObserver not supported)

## 维护说明 (Maintenance Notes)

1. 定期更新热门搜索词列表，确保反映用户实际需求
2. 根据用户反馈调整搜索建议内容
3. 监控搜索日志，优化无结果处理逻辑

1. Regularly update the popular searches list to reflect actual user needs
2. Adjust search suggestion content based on user feedback
3. Monitor search logs to optimize no-results handling logic
