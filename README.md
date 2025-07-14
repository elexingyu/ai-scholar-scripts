# AI Scholar Scripts: Zotero 数据转换工具集

本项目包含一系列 Python 脚本，旨在将各种来源的学术相关数据（如科研基金、新闻、播客、社交媒体帖子和视频）转换为 Zotero 兼容的 CSL JSON 格式。这使得研究人员可以轻松地将多样化的信息整合到他们的文献管理库中。

## 功能

- **多源支持**: 支持从 NIH 科研基金、新闻、播客、Twitter 和 YouTube 等多种来源导入数据。
- **标准化输出**: 所有脚本均生成 CSL JSON 文件，可直接导入 Zotero。
- **易于定制**: 脚本基于 Python 标准库，无需安装外部依赖，易于理解和修改。

## 脚本列表

- `grant_to_zotero_converter.py`: 将 NIH 基金数据（CSV 格式）转换为 Zotero 条目。
- `news_to_zotero_converter.py`: 将新闻搜索结果（CSV 格式）转换为 Zotero 网页条目。
- `podcast_to_zotero_converter.py`: 将播客元数据（CSV 格式）转换为 Zotero 音频条目。
- `twitter_to_zotero_converter.py`: 将 Twitter 推文数据（JSON 格式）转换为 Zotero 社交媒体帖子条目。
- `youtube_to_zotero_converter.py`: 将 YouTube 视频数据（JSON 格式）转换为 Zotero 视频条目。

## 环境要求

- Python 3

本项目不依赖任何第三方库，所有脚本均使用 Python 标准库。

## 使用方法

1.  将你的数据文件（CSV 或 JSON）放置在项目目录中。
2.  在终端中，使用 `python` 命令运行相应的转换脚本，并将输入文件路径作为参数。

    ```bash
    python [脚本文件名] [你的输入文件]
    ```

    例如:
    ```bash
    # 处理基金数据
    python grant_to_zotero_converter.py 'lisa-barrett-grant.csv'

    # 处理推文数据
    python twitter_to_zotero_converter.py 'path/to/your/tweets.json'
    ```
3.  脚本执行成功后，会在输入文件所在的目录中生成一个对应的 `.json` 文件。例如，`lisa-barrett-grant.csv` 将生成 `lisa-barrett-grant-csl.json`。
4.  (可选) 你也可以使用 `-o` 或 `--output_file` 参数来指定自定义的输出文件路径和名称：
    ```bash
    python youtube_to_zotero_converter.py 'videos.json' -o 'custom_youtube_zotero.json'
    ```

## 如何导入 Zotero

1.  打开 Zotero 桌面应用。
2.  在菜单栏选择 `文件` -> `导入...`。
3.  选择 `一个文件` 并点击 `下一步`。
4.  找到并选择你刚刚生成的 `.json` 文件。
5.  Zotero 会将文件中的所有条目导入到你的资料库中。 