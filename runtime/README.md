# 日本語の先頭文字の表示修正

ブックイベントやエピローグでは、ゲームが段落の最初の文字へ専用フォント・拡大率・縦位置の指定を足します。日本語の先頭文字が欠けたり、本文からずれたりするため、日本語設定のときだけこの装飾を省きます。本文・リンク・既存のタグはそのまま返します。

配布ZIPの `RTJP_Japanese/Assemblies/RTJP.DisplayFix.dll` がこの処理を担当します。追加のMODや設定は不要です。Owlcat標準の起動処理とゲーム内蔵のHarmonyを使います。ゲームのDLLは同梱しません。

## ビルド

.NET SDKと、手元のゲームの `WH40KRT_Data/Managed` を使います。

```powershell
$env:GameManagedDir = 'ゲームの場所/WH40KRT_Data/Managed'
dotnet build runtime/RTJP.DisplayFix.csproj -c Release -o 'リポジトリ外の出力先'
```

生成された `RTJP.DisplayFix.dll` を、パッケージ作成時の `--display-fix` に指定します。翻訳JSONと同じく、バイナリはGitへ入れません。

```sh
python -B tools/package_release.py --localization "外部のjaJP.json" --display-fix "外部のRTJP.DisplayFix.dll" --version 0.1.7 --output "外部の配布ZIP"
```

ロケールの切り替え・タグや改行の保持・起動処理の失敗時の扱いは、ゲームとHarmonyのAPIを代用したテストで確認します。実際の描画確認とは別の検証です。

```sh
dotnet run --project runtime-tests/RTJP.DisplayFix.Tests.csproj -c Release
```

仕組みの参照先：[Owlcat公式のエントリポイントとHarmonyの説明](https://github.com/OwlcatOpenSource/RTModificationTemplate#assembly-entry-point)。
