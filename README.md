# my-synapse-components

## コンポーネント追加手順

1. ディレクトリ作成
```
mkdir sample-component
```

1. uvの初期化と必要なパッケージインストール
```
uv init
uv add click
uv add speedbeesynapse-sccde
uv add taskipy
```

1. taskの設定
pyproject.tomlに以下を追加
```
[tool.taskipy.tasks]
build = "task build_vue && task pack"
dev = "task build_vue && uv run sccde serve --port 8123 --reload"
build_vue = "cd parameter_ui/opcua-server && npm install && npm run build"
pack = "uv run sccde make-package"
lint = "uvx ruff check source"
clean = "uv run build.py clean"
```

1. sccdeの初期化
```
uv run sccde init
```

※初期化後は、scc-info.jsonなどがサンプルのものになっているので変更する。

1. UIの初期化
```
cd parameter_ui
create-speedbeesynapse-ui opcua-server
```

※create-speedbeesynapse-uiは事前にインストールが必要。

