# GitHub Actions 工作流说明

本目录包含项目的GitHub Actions自动化工作流配置。

## 工作流列表

### 1. deploy.yml - 自动部署工作流

**功能**: 自动构建MkDocs站点并部署到GitHub Pages

**触发条件**:
- **自动触发**: 推送到 `main` 分支时
  - 仅在以下文件变更时触发（优化构建效率）：
    - `docs/**` - 文档内容
    - `mkdocs.yml` - MkDocs配置
    - `requirements.txt` - Python依赖
    - `.github/workflows/deploy.yml` - 工作流配置
- **手动触发**: 通过GitHub Actions界面或CLI手动运行

**工作流程**:

#### 构建阶段 (Build Job)
1. **检出代码**: 使用 `actions/checkout@v4` 获取完整Git历史
2. **设置Python环境**: Python 3.11，启用pip缓存
3. **安装依赖**: 从 `requirements.txt` 安装所有Python包
4. **配置Git**: 为git-revision-date插件配置用户信息
5. **构建站点**: 运行 `mkdocs build --strict --verbose`
   - `--strict`: 将所有警告视为错误
   - `--verbose`: 输出详细构建信息
6. **添加版本标识**: 创建包含构建信息的标识文件
7. **上传产物**: 将构建的 `site/` 目录上传为GitHub Pages产物

#### 部署阶段 (Deploy Job)
1. **部署到GitHub Pages**: 使用 `actions/deploy-pages@v4`
2. **输出部署信息**: 显示部署成功消息和站点URL

**权限配置**:
- `contents: read` - 读取仓库内容
- `pages: write` - 写入GitHub Pages
- `id-token: write` - 用于OIDC认证

**并发控制**:
- 使用 `concurrency` 确保同一时间只有一个部署运行
- 不取消正在进行的部署（`cancel-in-progress: false`）

**环境变量**:
- `ENABLE_PDF_EXPORT: false` - 禁用PDF导出以加快构建速度

**输出文件**:
- 构建的静态站点: `site/` 目录
- 离线版本标识: `site/OFFLINE_BUILD.html`
  - 包含构建时间（UTC）
  - Git提交哈希（短格式）
  - Git分支名称

**部署目标**:
- GitHub Pages环境
- URL: https://x-gen-lab.github.io/medical-embedded-knowledge/

## 使用说明

### 查看工作流运行状态

1. 访问仓库的 **Actions** 标签页
2. 选择 **Deploy to GitHub Pages** 工作流
3. 查看最近的运行记录和日志

### 手动触发部署

**方法1: GitHub网页界面**
1. 访问 Actions → Deploy to GitHub Pages
2. 点击 "Run workflow" 按钮
3. 选择分支（通常是 `main`）
4. 点击 "Run workflow" 确认

**方法2: GitHub CLI**
```bash
gh workflow run deploy.yml
```

**方法3: 传统方式**
```bash
mkdocs gh-deploy
```

### 调试构建问题

如果构建失败，请检查：

1. **查看工作流日志**: 在Actions页面点击失败的运行查看详细日志
2. **本地复现**: 在本地运行相同的构建命令
   ```bash
   mkdocs build --strict --verbose
   ```
3. **检查依赖**: 确保 `requirements.txt` 中的所有依赖都已正确安装
4. **验证配置**: 检查 `mkdocs.yml` 配置文件是否有语法错误
5. **检查文档**: 运行验证脚本检查文档格式
   ```bash
   python scripts/validate_markdown.py
   ```

### 优化构建速度

当前配置已包含以下优化：

- ✅ **pip缓存**: 缓存Python依赖以加快安装速度
- ✅ **路径过滤**: 仅在文档相关文件变更时触发
- ✅ **禁用PDF导出**: 跳过耗时的PDF生成（可按需启用）
- ✅ **并发控制**: 避免重复构建

如需进一步优化：

1. **启用增量构建**: 考虑使用缓存机制缓存构建产物
2. **并行构建**: 如果有多个独立的构建任务，可以并行执行
3. **条件执行**: 根据变更的文件类型执行不同的构建步骤

## 维护指南

### 更新工作流

修改 `.github/workflows/deploy.yml` 文件后：

1. 提交更改到仓库
2. 工作流会在下次触发时使用新配置
3. 可以手动触发测试新配置

### 更新依赖

更新Python依赖时：

1. 修改 `requirements.txt`
2. 在本地测试构建
3. 提交更改
4. 工作流会自动使用新依赖

### 更改部署目标

如需部署到其他平台（Netlify、Vercel等）：

1. 创建新的工作流文件（如 `deploy-netlify.yml`）
2. 使用相应平台的GitHub Actions
3. 配置必要的密钥和环境变量

## 故障排除

### 常见问题

**问题1: 构建失败 - "No module named 'mkdocs'"**
- **原因**: 依赖安装失败
- **解决**: 检查 `requirements.txt` 是否正确，确保所有依赖都已列出

**问题2: 部署失败 - "Permission denied"**
- **原因**: GitHub Pages权限未正确配置
- **解决**: 检查仓库设置 → Pages → Source 是否设置为 "GitHub Actions"

**问题3: 站点404错误**
- **原因**: 站点URL配置不正确
- **解决**: 检查 `mkdocs.yml` 中的 `site_url` 配置

**问题4: 构建超时**
- **原因**: 构建时间过长（超过GitHub Actions限制）
- **解决**: 
  - 禁用PDF导出
  - 减少构建内容
  - 优化插件配置

**问题5: Git历史获取失败**
- **原因**: `fetch-depth: 0` 在大型仓库中可能很慢
- **解决**: 如果不需要完整历史，可以设置 `fetch-depth: 1`

### 获取帮助

如果遇到其他问题：

1. 查看 [GitHub Actions文档](https://docs.github.com/en/actions)
2. 查看 [MkDocs部署文档](https://www.mkdocs.org/user-guide/deploying-your-docs/)
3. 在项目Issue中提问
4. 联系项目维护者

## 最佳实践

1. **定期检查工作流**: 确保工作流正常运行
2. **监控构建时间**: 如果构建时间过长，考虑优化
3. **保持依赖更新**: 定期更新GitHub Actions和Python依赖
4. **测试后部署**: 在本地测试通过后再推送到main分支
5. **使用分支保护**: 配置分支保护规则，要求CI通过后才能合并

## 相关资源

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [GitHub Pages文档](https://docs.github.com/en/pages)
- [MkDocs部署指南](https://www.mkdocs.org/user-guide/deploying-your-docs/)
- [Material for MkDocs部署](https://squidfunk.github.io/mkdocs-material/publishing-your-site/)

---

**最后更新**: 2026-02-09  
**维护者**: 医疗器械嵌入式软件知识体系团队
