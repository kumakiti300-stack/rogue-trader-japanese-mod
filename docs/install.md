# 導入・更新・取り外し

翻訳を含む配布ZIPを使う、Windows向けの手順です。配布状況は[README](../README.md)で確認してください。
対応ゲーム版、確認済みの範囲、既知の問題は各Releaseの案内で確認してください。

翻訳ファイルは配布ZIPに含めます。GitHubの「Code → Download ZIP」で取得するリポジトリのファイルだけでは導入できません。

## 導入

1. ゲームを完全に終了します。
2. 配布ZIPを展開し、中の `RTJP_Japanese` フォルダを次の場所へコピーします。`Modifications` フォルダがなければ作成してください。

   ```text
   %USERPROFILE%\AppData\LocalLow\Owlcat Games\Warhammer 40000 Rogue Trader\Modifications
   ```

   コピー後は次の配置にします。`RTJP_Japanese` フォルダを二重に入れないでください。

   ```text
   Modifications/
     RTJP_Japanese/
       OwlcatModificationManifest.json
       OwlcatModificationSettings.json
       Localization/
         jaJP.json
   ```

3. 次の設定ファイルをテキストエディターで開き、`EnabledModifications` に `"RTJP_Japanese"` を追加して保存します。他のMODの項目は残してください。旧試験版を使っていた場合は `"RTJP_Japanese_Trial"` を外し、試験版と配布版を同時に有効化しないでください。編集前に設定ファイルのコピーを取っておくと元に戻せます。

   ```text
   %USERPROFILE%\AppData\LocalLow\Owlcat Games\Warhammer 40000 Rogue Trader\OwlcatModificationManagerSettings.json
   ```

   設定ファイルがない場合は、次の内容で作成します。すでに他のMODの設定がある場合は、ファイル全体を置き換えず、既存の配列へ追加してください。

   ```json
   {
     "EnabledModifications": ["RTJP_Japanese"]
   }
   ```

   有効化に使う名前は、配布MODのmanifestの `UniqueName` である `RTJP_Japanese` です。この設定方法は[Owlcat公式のMOD手順](https://github.com/OwlcatOpenSource/RTModificationTemplate)に基づいています。

4. ゲームを起動し、言語を日本語に設定して、対象の文章を確認します。

ゲーム本体の日本語ファイルを上書きする必要はありません。未修正の箇所にはゲームの既存日本語が表示されます。

## 更新

ゲームを終了してから、新しい配布ZIPの `RTJP_Japanese` フォルダで導入済みの同名フォルダを上書きします。
有効化の設定が済んでいれば、通常は `EnabledModifications` を編集し直す必要はありません。Releaseに別の更新手順がある場合は、そちらに従ってください。
更新後はゲームを起動し直してください。

## 無効化・取り外し

ゲームを終了し、`OwlcatModificationManagerSettings.json` の `EnabledModifications` から `"RTJP_Japanese"` だけを削除して保存します。他のMODの項目は残してください。
完全に取り外す場合は、さらに `Modifications` 内の `RTJP_Japanese` フォルダを削除します。ゲーム本体やセーブのファイルは削除しません。

## 他のMODとの併用

別の翻訳MODが同じ文章を置き換える場合、読み込み順によって一方の訳が優先されます。想定した訳にならないときは、他の翻訳MODを無効化して確認してください。
表示の問題が続く場合は、併用している翻訳MODやフォントMODの名前を添えて[報告してください](reporting.md)。

## 確認範囲

配布用パッケージでのゲーム内確認は未実施です。静的なファイル検査や、既存の試験版での適用・初期化の確認は、全会話の表示や進行の確認とは別です。
全会話・全分岐のプレイ確認は完了していません。配布時の確認範囲は各Releaseの案内に記載します。

[READMEへ戻る](../README.md)
