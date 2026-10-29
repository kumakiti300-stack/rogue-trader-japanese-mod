# 配布パッケージの作成

翻訳JSONはこのリポジトリへ保存せず、配布用ZIPだけに含めます。ZIPとチェックサムはGitに登録せず、配布時にReleasesのアセットとして添付します。
GitHubが自動生成する「Source code」のZIPには、このリポジトリの内容だけが入るため、翻訳MODの導入用には使えません。

v0.1.0は試験版の下書きとして準備しています。Releaseは未公開で、リポジトリはPrivateのままです。

## 用意するもの

- Python 3.11以降とGit。追加のPythonパッケージは不要です。
- 開発側で校正・QAを済ませた、Owlcat形式の `jaJP.json`。リポジトリ外に置いてください。
- 配布版番号、対応ゲーム版、確認範囲、既知の問題。

このツールは翻訳の選別や校正をしません。入力されたJSONの全文を、そのままZIPに収録します。
開発側の試験出力を使う場合も、配布する訳の選定とパッケージの版番号・識別名は別に判断してください。

## 検査とZIP作成

リポジトリのルートで実行します。
検査対象はGitの追跡ファイルと履歴です。ファイルを追加した場合は、配布対象のファイルだけをステージしてから検査し、コミット後にも再実行してください。

```powershell
py -3 -B tools/check_repository.py --history
py -3 -B -m unittest discover -s tests -v

$translation = Read-Host 'リポジトリ外のjaJP.jsonのパス'
$version = Read-Host '配布版番号（数字3区切り、例 0.1.0）'
$archive = Join-Path (Read-Host 'ZIPを保存するフォルダ') "rogue-trader-japanese-$version.zip"
py -3 -B tools/package_release.py --localization $translation --version $version --output $archive
```

指定先へZIPと、その隣に `.zip.sha256` を作成します。同名ファイルは上書きしません。
入力JSONの基本構造とZIPのCRCは確認しますが、ゲーム内の表示や進行の確認は別に必要です。

ZIPには次の構造を含めます。

```text
RTJP_Japanese/
  OwlcatModificationManifest.json
  OwlcatModificationSettings.json
  Localization/jaJP.json
  Assemblies/
  Bundles/
  Blueprints/
  README.md
  NOTICE.md
  docs/install.md
  docs/reporting.md
```

`UniqueName` は `RTJP_Japanese` です。manifestの版番号は、コマンドで指定した値に置き換えます。
ゲーム本体のDLL、フォント、他のMOD、開発側のコーパスや作業履歴はパッケージへ含めません。フォントMODは任意で、翻訳JSONの読み込みには必要ありません。

## 配布時

READMEの配布状況と、導入案内の確認範囲を実際の配布内容に合わせて更新します。
下書きを公開したら、READMEの下書き・未公開の表示も改めます。Releases一覧へのリンクはそのまま使用できます。
確認したコミットに対応するタグを用意し、ZIPと `.sha256` をReleaseへ添付します。案内には対応ゲーム版、確認範囲、既知の問題を記載してください。
「Source code」の自動生成ZIPと、添付したMOD用ZIPを区別して案内します。

リポジトリがPrivateの間は、閲覧権限のある人だけがReleaseを参照できます。一般公開への切り替えとReleaseの公開は、別途判断します。
パッケージ作成コマンドは、アップロード、タグ・Releaseの作成、リポジトリの公開設定変更、ゲーム操作を行いません。

[GitHubのReleasesの説明](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) / [READMEへ戻る](../README.md)
