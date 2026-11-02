# 導入・更新・取り外し

翻訳を含む[MOD用ZIP](https://github.com/kumakiti300-stack/rogue-trader-japanese-mod/releases/latest)を使う、Windows向けの手順です。
対象のゲーム版と更新内容は各Releaseの案内で確認してください。

翻訳ファイルは配布ZIPに含めます。GitHubの「Code → Download ZIP」で取得するリポジトリのファイルだけでは導入できません。

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

手動で更新する場合は、ゲームとMOD管理ツールを終了してから、新しい配布ZIPの `RTJP_Japanese` フォルダで導入済みの同名フォルダを上書きします。
有効化の設定が済んでいれば、通常は `EnabledModifications` を編集し直す必要はありません。Releaseに別の更新手順がある場合は、そちらに従ってください。
更新後はゲームを起動し直してください。

## 無効化・取り外し

ModFinder RTで管理している場合は、ModFinder RTから無効化・削除してください。

手動の場合は、ゲームとMOD管理ツールを終了してから操作します。

`OwlcatModificationManagerSettings.json` の `EnabledModifications`・`ActiveModifications`・`DisabledModifications` に `"RTJP_Japanese"` があれば、その項目だけ削除して保存します。ほかのMODの項目は残してください。
完全に取り外す場合は、さらに `Modifications` 内の `RTJP_Japanese` フォルダを削除します。ゲーム本体やセーブのファイルは削除しません。

## 他のMODとの併用

別の翻訳MODが同じ文章を置き換える場合、読み込み順によって一方の訳が優先されます。想定した訳にならないときは、他の翻訳MODを無効化して確認してください。
表示の問題が続く場合は、併用している翻訳MODやフォントMODの名前を添えて[報告してください](reporting.md)。

## 動作確認

制作者が実機で動作を確認しています。対象のゲーム版と更新内容は[最新Release](https://github.com/kumakiti300-stack/rogue-trader-japanese-mod/releases/latest)で確認できます。

手順の参照先：[ModFinder RTの配布元](https://github.com/CasDragon/ModFinder)、[Owlcat公式のMOD手順](https://github.com/OwlcatOpenSource/RTModificationTemplate)。

[READMEへ戻る](../README.md)
