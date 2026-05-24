# Submission Checklist

提交前逐项确认。

## 仓库

- [ ] 仓库已在开题后创建。
- [ ] 仓库提交截止后可公开访问。
- [ ] README 放在仓库根目录。
- [ ] README 包含 Demo 视频链接。
- [ ] README 包含启动方式、测试方式、第三方依赖和原创说明。
- [ ] PR 描述不为空，并包含功能描述、实现思路、测试方式。
- [ ] commit 时间戳落在开发周期内。
- [ ] 没有最后一天一次性导入全部代码。

## 功能

- [ ] 可以启动前端和后端。
- [ ] 可以选择示例场景并生成素材。
- [ ] 可以保存和应用项目风格包。
- [ ] 生成结果显示增强 Prompt、约束标签和质量检查。
- [ ] 可以导出单张 PNG。
- [ ] 可以导出 ZIP。
- [ ] ZIP 中包含 `images/`、`spritesheet/`、`metadata.json`、`engine-import-guide.md`。
- [ ] `spritesheet.json` 包含帧坐标和源文件映射。

## 验证命令

```powershell
npm --prefix frontend run build
.\.conda\python.exe -m pytest backend\tests -q
.\.conda\python.exe -m compileall backend\app
```

## Demo 视频

- [ ] 视频有声音讲解。
- [ ] 覆盖一个完整示例场景。
- [ ] 展示生成、质量检查、导出 ZIP。
- [ ] 展示 ZIP 结构和 `spritesheet.json`。
- [ ] 说明当前使用本地生成器保证稳定，后续可替换真实图像模型。
- [ ] 视频链接放在 README 显眼位置。
