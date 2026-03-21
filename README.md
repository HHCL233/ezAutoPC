## ezAutoPC

使用多模态AI自动化PC操作。

### 注意事项

- BUG较多
- 部分场景只针对Linux
- 配置不方便

### 使用

1. Clone仓库
2. `uv sync`
3. 修改 config.json 中的 BASE_URL、MODEL、API_KEY
4. `cd dashboard`
5. `npm install`
6. `npm run build`
7. `cd ..`
8. `uv run main.py`