# Rogue Trader 日本語再翻訳MOD

バージョン: {{VERSION}}

『Warhammer 40,000: Rogue Trader』の会話・地の文・選択肢・能力説明などを、英語原文から訳し直す非公式MODです。Windows版向けです。
AIを使って翻訳・校正し、制作者が実機で動作を確認しています。翻訳の照合にはゲーム1.6.1.514のデータを使用しています。

## 導入

### ModFinder RTを使う場合

すでにModFinder RTを使っている場合は、こちらの手順で入れてください。

1. ゲームを完全に終了します。
2. ダウンロードしたMOD用ZIPを**展開せず**、ModFinder RTの **Drag zips here to install** へドラッグします。
3. 一覧の **Rogue Trader Japanese** を有効にします。
4. ゲームを起動し、言語を日本語に設定します。

ファイルの配置と有効化はModFinder RTに任せます。この手順では、設定JSONを手で編集する必要はありません。
手動ですでに配置している場合も、ModFinder RTを開き直して一覧から有効化してください。

### 手動で入れる場合

1. **ゲームとModFinder RTなどのMOD管理ツールを完全に終了**し、配布ZIPを展開します。
2. **Win＋R**を押し、次の場所を開きます。

   ```text
   %USERPROFILE%\AppData\LocalLow\Owlcat Games\Warhammer 40000 Rogue Trader
   ```

3. その中の `Modifications` フォルダへ、展開した `RTJP_Japanese` フォルダを丸ごとコピーします。`Modifications` がなければ作成してください。

   主なファイルは次の配置になります。フォルダを二重に入れないでください。

   ```text
   Modifications/
     RTJP_Japanese/
       OwlcatModificationManifest.json
       OwlcatModificationSettings.json
       Assemblies/
       Blueprints/
       Bundles/
       Localization/
         jaJP.json
       README.md
   ```

   `Assemblies`・`Blueprints`・`Bundles` は空のままで正常です。フォルダごとコピーしてください。

4. 手順2で開いた場所の `OwlcatModificationManagerSettings.json` を、メモ帳などで開きます。編集前にコピーを保存しておくと元に戻せます。

   既存の設定とほかのMODの項目を残して、次のように編集します。

   - `EnabledModifications` に `"RTJP_Japanese"` を追加します。
   - `ActiveModifications` がある場合は、そこにも `"RTJP_Japanese"` を追加します。
   - `DisabledModifications` に `"RTJP_Japanese"` がある場合は、その項目だけ削除します。

   設定ファイルがない場合だけ、次の内容で新しく作成します。既存のファイル全体をこの内容で置き換えないでください。

   ```json
   {
     "EnabledModifications": ["RTJP_Japanese"],
     "ActiveModifications": ["RTJP_Japanese"],
     "DisabledModifications": []
   }
   ```

   ファイル名が `OwlcatModificationManagerSettings.json.txt` になっていないことも確認してください。
   旧試験版を使っていた場合は `"RTJP_Japanese_Trial"` を`EnabledModifications` と `ActiveModifications` から外し、配布版と同時に有効化しないでください。

5. 保存してからゲームを起動し、言語を日本語に設定します。

### 導入できたか確認

**タイトル画面で「次へ」が「コンティニュー」になっていれば、導入成功です。**

ゲーム本体のファイルを上書きする必要はありません。差し替え対象外の文章はゲームの日本語で表示されます。

### Unity Mod Managerとの併用

本MODはゲーム標準のOwlcat形式です。ModFinder RTはこの形式も扱えますが、UMM形式のMODとは配置先・有効化の画面が異なります。

- 本MOD：`Modifications` に配置。ゲーム標準のMOD画面は **Shift＋F10**。
- UMM形式のMOD：`UnityModManager` に配置。UMMの画面は **Ctrl＋F10**。

UMMの一覧に本MODが表示されなくても、UMM用フォルダへ移し直す必要はありません。導入の確認には、上のタイトル画面の表示を使ってください。
本作にはUMMが内蔵されているため、UMM本体を別途導入してゲームをパッチする必要はありません。

## 更新

ModFinder RTで導入した場合は、新しいZIPもModFinder RTへドラッグして更新してください。無効化・削除もModFinder RTから行えます。

手動で更新する場合は、ゲームとMOD管理ツールを終了してから、新しいZIPの `RTJP_Japanese` フォルダで、導入済みの同名フォルダを上書きします。有効化の設定はそのまま使えます。

訳を自分で直している場合は、更新前に `Localization/jaJP.json` のコピーを保存してください。更新すると、編集した内容も新しいファイルで置き換わります。

## 無効化・取り外し

ModFinder RTで管理している場合は、ModFinder RTから無効化・削除してください。

手動の場合は、ゲームとMOD管理ツールを終了してから操作します。

`OwlcatModificationManagerSettings.json` の `EnabledModifications`・`ActiveModifications`・`DisabledModifications` に `"RTJP_Japanese"` があれば、その項目だけ削除して保存します。ほかのMODの項目は残してください。

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

## 翻訳方針

英語原文の意味を保ち、会話は人物らしく、地の文は自然に読める日本語に整えます。用語は次の優先順位で判断します。

1. **GW公式訳に準拠する。** Games Workshopの公式日本語訳に既存の用例がある語は、原則としてその訳を使います。例：Psyker → サイカー。
2. **ハイゴシックと40k固有用語は音写する。** 作中世界の固有名詞・称号・施設名は、カタカナで原語の形を残します。特に造語の称号は、仕事の内容を表す日本語に置き換えません。例：Infernus Master → インフェルヌス・マスター、Vox Master → ヴォクス・マスター、Statio Medicae → スタティオ・メディカエ、High Factotum → ハイ・ファクトータム。
3. **機能が意味を持つ箇所は機能訳する。** システム用語・数値・パラメータなど、意味をすぐ理解する必要があるものは、機能に即した日本語にします。例：Momentum → 戦意、Deflection（値）→ ダメージ軽減値。Momentumを「推進力」とするような、効果を誤解させる直訳は使いません。
4. **同じ原語でも文脈で訳し分ける。** 技能・システムでの用法は機能訳、固有名詞としての用法は音写します。例：Medicaeの技能名・判定・計算式は「医術」、役職・施設・器具などの呼び名は「メディカエ」。

迷ったときは1 → 2 → 3の順に確認します。どれにも明確に当てはまらない場合は、推測で確定せず、候補として扱います。

「ゲーム公式訳と同じ」という理由だけで正しいとは判断しません。GW公式日本語の用例とは区別し、原語の綴り、意味、場面やゲーム内の機能も照合します。

### 訳し分けの例

| 原語・用法 | MOD表記 |
|---|---|
| Medicae：技能・判定 | 医術 |
| Medicae Officer：役職 | メディカエ士官 |
| Statio Medicae：固有の施設名 | スタティオ・メディカエ |
| High Factotum：正式な称号 | ハイ・ファクトータム |
| Factotum：原文で短く呼ぶ場合 | ファクトータム |
| Infernus Master / Vox Master | インフェルヌス・マスター／ヴォクス・マスター |
| Manufactorum：施設の種類 | 聖工場 |
| Manufactorum Medicae：固有の施設名 | マニュファクトルム・メディカエ |

「聖工場」「技術司祭」「製造総司令」のように、GW公式日本語に用例がある訳は原則1に従って使います。一般の職業・説明文と、固有の称号も区別します。

詳しい方針と出典は[Web版](https://github.com/kumakiti300-stack/rogue-trader-japanese-mod/blob/main/docs/translation-policy.md)を参照してください。

## 関連情報

- [導入・更新・取り外しの別冊](docs/install.md)
- [報告の手順](docs/reporting.md)
- [配布ページ・更新情報](https://github.com/kumakiti300-stack/rogue-trader-japanese-mod/releases)
- [権利表記](NOTICE.md)
