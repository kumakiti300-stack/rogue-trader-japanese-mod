# Rogue Trader 日本語再翻訳MOD

バージョン: {{VERSION}}

『Warhammer 40,000: Rogue Trader』の会話・地の文・選択肢・能力説明などを、英語原文から訳し直す非公式MODです。Windows版向けです。
AIを使って翻訳・校正し、制作者が実機で動作を確認しています。翻訳の照合にはゲーム1.6.1.514のデータを使用しています。

## ハイゴシック風の呼び名について

ゲーム中の言語名High Gothicは「上級ゴシック語」としています。

技能・判定・計算式や通常の説明では、意味が分かる日本語を優先します。人物の役職や固有の施設・器具など、世界観上の呼び名を残す場合はカタカナにします。

- **Medicae**：技能や判定では「医術」、人物・施設・器具などの呼び名では「メディカエ」。Medicae Officerは「メディカエ士官」です。
- **Infernus Master / Vox Master**：「インフェルヌス・マスター」「ヴォクス・マスター」。この2つの役職名は、呼び名全体をカタカナで残します。
- **Manufactorum**：施設の種類や通常の説明では「聖工場」、固有の施設名Manufactorum Medicaeでは「マニュファクトルム・メディカエ」。
- **Statio Medicae**：固有の施設名として「スタティオ・メディカエ」。

「帝国行政局」のように、既に日本語名を採用している組織・役職などは、その表記を使います。

## 導入

1. ゲームを完全に終了し、配布ZIPを展開します。
2. **Win＋R**を押し、次の場所を開きます。

   ```text
   %USERPROFILE%\AppData\LocalLow\Owlcat Games\Warhammer 40000 Rogue Trader
   ```

3. その中の `Modifications` フォルダへ、展開した `RTJP_Japanese` フォルダを丸ごとコピーします。`Modifications` がなければ作成してください。

   主なファイルが次の位置にあることを確認します。フォルダを二重に入れないでください。

   ```text
   Modifications/
     RTJP_Japanese/
       OwlcatModificationManifest.json
       OwlcatModificationSettings.json
       Localization/
         jaJP.json
       README.md
   ```

4. 手順2で開いた場所にある `OwlcatModificationManagerSettings.json` を、メモ帳などのテキストエディターで開きます。編集前にファイルのコピーを保存しておくと元に戻せます。

   `EnabledModifications` の配列に `"RTJP_Japanese"` を追加して保存してください。他のMODの項目は残し、項目の間はカンマで区切ります。

   設定ファイルがない場合は、次の内容で新しく作成します。すでにあるファイルを、この内容で丸ごと置き換えないでください。

   ```json
   {
     "EnabledModifications": ["RTJP_Japanese"]
   }
   ```

   新規作成したファイルの名前が `OwlcatModificationManagerSettings.json.txt` になっていないことも確認してください。

   旧試験版を使っていた場合は、配列から `"RTJP_Japanese_Trial"` を外して、配布版の `"RTJP_Japanese"` を有効にしてください。

5. ゲームを起動し、言語を日本語に設定します。

ゲーム本体のファイルを上書きする必要はありません。差し替え対象外の文章は、ゲームの日本語で表示されます。

## 更新

ゲームを終了してから、新しいZIPの `RTJP_Japanese` フォルダで、導入済みの同名フォルダを上書きします。有効化の設定はそのまま使えます。

訳を自分で直している場合は、更新前に `Localization/jaJP.json` のコピーを保存してください。更新すると、編集した内容も新しいファイルで置き換わります。

## 無効化・取り外し

ゲームを終了し、`OwlcatModificationManagerSettings.json` の `EnabledModifications` から `"RTJP_Japanese"` だけを削除して保存します。他のMODの項目は残してください。

完全に取り外す場合は、さらに `Modifications` 内の `RTJP_Japanese` フォルダを削除します。

## 訳を自分で直す

気に入らない訳は、自由に書き換えて使ってください。事前の連絡や確認は不要です。

編集するファイルは、導入した `RTJP_Japanese/Localization/jaJP.json` です。

1. ゲームを終了し、編集前のファイルをコピーして保存します。
2. テキストエディターでファイルを開き、直したい文章を検索します。
3. 該当する項目の `"Text"` に入っている文章を書き換え、UTF-8で保存します。
4. ゲームを起動して表示を確認します。

識別IDや `"Offset"` は変更せず、文章中の `{name}` などの変数や、`{g|...}`・`{/g}`・`<b>` などのタグは残してください。文章中の改行は `\n` と書きます。JSONのカンマや引用符も保ってください。

## 表示がおかしいとき

- `RTJP_Japanese` フォルダが二重になっていないか、上の配置例と比べてください。
- 設定ファイルの `EnabledModifications` に `"RTJP_Japanese"` が入っているか確認してください。
- 別の翻訳MODが同じ文章を変更している場合は、読み込み順によって表示される訳が変わります。他の翻訳MODを無効にして確認してください。

気になる訳や表示は、[GitHubのIssues](https://github.com/kumakiti300-stack/rogue-trader-japanese-mod/issues/new/choose)へ報告できます。場所・会話相手・実際の文章と、前後の状況が分かるスクリーンショットがあると探しやすくなります。

## 関連情報

- [導入・更新・取り外しの別冊](docs/install.md)
- [報告の手順](docs/reporting.md)
- [配布ページ・更新情報](https://github.com/kumakiti300-stack/rogue-trader-japanese-mod/releases)
- [権利表記](NOTICE.md)
