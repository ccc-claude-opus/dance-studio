# 真人動捕舞蹈教室 / Motion-Capture Dance Studio

用 3D 舞者示範各種舞蹈：真人動作捕捉、依舞步規則生成的國標舞、從你自己的影片抓出的動作。介面有中文和英文。

* 展示頁 -- https://ccc-claude-opus.github.io/dance-studio/

## 資料夾結構

```
dance-studio/
├── README.md
├── server.py                    選用的本機伺服器：提供網頁並把相機錄影存到 recordings/
├── .github/workflows/pages.yml  把 web/ 發佈到 gh-pages 分支
├── web/                         網頁本體（直接放到任何靜態網站主機即可）
│   ├── index.html               主程式：舞台、控制、音樂、影片、練習功能
│   ├── meta.js                  舞種清單、橋段名稱與說明（中英）、每段的速度
│   ├── data_<舞種>.js           各舞種的關節軌跡資料（點選時才載入）
│   ├── music.js                 即時合成的伴奏，以及線上真實錄音的曲目清單
│   ├── capture.js               從影片抓動作（MediaPipe 姿勢辨識）
│   ├── camera.js                相機即時骨架、錄影與回放，以及和 server.py 溝通
│   ├── vision_bundle.mjs        MediaPipe Tasks Vision 0.10.21
│   ├── vision_wasm_internal.js  MediaPipe WASM 載入器
│   ├── vision_wasm_internal.wasm
│   ├── pose_model.js            姿勢辨識模型（pose_landmarker_lite，base64）
│   ├── michelle.js              女舞者模型（base64 glTF）
│   └── rpm.js                   男舞者模型（base64 glTF）
└── tools/                       重新產生 web/ 資料用的 Python 腳本
    ├── build2.py                主建置：讀 BVH、偵測薩爾薩橋段、生成國標舞，輸出 meta.js 與 data_*.js
    ├── bvh.py                   BVH 讀取與正向運動學
    ├── lib.py                   把各種骨架對應到網頁用的 22 個關節
    ├── tempo.py                 從腳步估算舞蹈速度（BPM）
    ├── gen.py                   生成動作的引擎：腳步、重心、IK、平滑化
    ├── choreo.py                巴恰塔、吉魯巴的舞步編排
    ├── ballroom.py              國標舞十支（標準舞五支、拉丁舞五支）的舞步編排
    ├── make_assets.py           從 assets/ 重新產生 michelle.js、rpm.js、pose_model.js
    └── assets/                  人物模型、姿勢模型、芭蕾單足旋轉 BVH 原始檔
```

## 在自己電腦上執行

（想要存相機錄影的話，改用下面「相機即時錄影」一節的 `python3 server.py`。）

網頁會用 ES 模組和 WASM，直接雙擊 index.html 開不起來，要用本機伺服器：

```bash
cd dance-studio/web
python3 -m http.server 8000
```

然後用瀏覽器開 http://localhost:8000 。

網頁需要連網一次，從 cdn.jsdelivr.net 載入 three.js 0.160.0，並從 Google Fonts 載入字型。

## 相機即時錄影

「相機即時錄影」區可以開啟電腦或手機的相機，即時在畫面上畫出辨識到的骨架（單人或雙人）。按「● 開始錄影」會同時錄下影像（WebM，Safari 為 MP4）和每一格的骨架座標，錄完可以：

- 回放：影像和骨架一起播放、暫停、拖曳；也可以關掉影像只看骨架。
- 放上舞台：把骨架轉成 3D 動作，用舞台上的舞者重播，滿意的話再加入某支舞的橋段（和「從影片抓動作」相同的流程）。
- 存到伺服器：只有用 `server.py` 開啟網頁時才會出現。

相機只能在 https 或 localhost 下使用，GitHub Pages 和本機都可以。

**沒有伺服器**（GitHub Pages、`python3 -m http.server`）：錄影、回放、放上舞台都能用，但錄影只存在記憶體裡，關閉頁面就消失。

**有伺服器**：在專案資料夾執行

```bash
python3 server.py
```

然後開 http://localhost:8000 。頁面會自動偵測到伺服器，錄影可以存檔，下次開啟會出現在「我的錄影」清單。每段錄影存成 `recordings/<id>/` 底下的 `meta.json`、`skeleton.json`（MediaPipe 33 個關節，影像座標與世界座標）和 `video.webm`。可用 `--port`、`--data`（存放位置）調整；要讓同一個網路的手機連線，加 `--host 0.0.0.0`，但手機瀏覽器只允許 https 網頁使用相機，所以這種情況需要另外架 https。`server.py` 只用 Python 標準函式庫，沒有帳號或權限控管，請只在自己的電腦或信任的網路上使用。

## 放上 GitHub Pages

`.github/workflows/pages.yml` 會在 main 上的 `web/` 有變動時，把 `web/` 原封不動推到 `gh-pages` 分支（也可以在 Actions 頁面手動執行 *Deploy to GitHub Pages*）。網頁沒有建置步驟，所有路徑都是相對路徑，放在子路徑下也能用。

第一次設定：

1. push 到 main，等 Actions 跑完，確認多了 `gh-pages` 分支。
2. 到 repo 的 **Settings → Pages**，Source 選 **Deploy from a branch**，分支選 `gh-pages`、資料夾 `/ (root)`。
3. 網址是 `https://<帳號>.github.io/<repo>/`，例如 https://ccc-claude-opus.github.io/dance-studio/ 。

如果 Actions 推送時出現權限錯誤，到 **Settings → Actions → General → Workflow permissions** 選 **Read and write permissions**。

## 重新建置資料（選用）

只有想改舞步、加舞種或調參數時才需要。需要 Python 3、numpy、scipy。

1. 下載 CMU 動作捕捉資料的 BVH 版本：
   ```bash
   cd dance-studio/tools
   git clone --depth 1 --filter=blob:none --sparse https://github.com/meshula/cmu-mocap.git cmu
   cd cmu && git sparse-checkout set data/005 data/055 data/060 data/061 data/085 data/090 data/093 data/094
   ```
2. 建置：
   ```bash
   cd dance-studio/tools
   python3 build2.py            # 輸出到 ../web/
   python3 make_assets.py       # 只有換了人物或姿勢模型才需要
   ```
   也可以用環境變數 `CMU_DIR` 指定 BVH 資料夾，用 `OUT_DIR` 指定輸出位置。

## 資料與授權

- 真人動作：CMU Graphics Lab Motion Capture Database（http://mocap.cs.cmu.edu/），BVH 轉檔來自 meshula/cmu-mocap。CMU 允許自由使用，請在作品中註明出處。
- 芭蕾單足旋轉 BVH、女舞者 Michelle、男舞者（Ready Player Me 頭像）：取自 three.js 範例資料（MIT 授權的專案中附帶的範例素材）。Michelle 與森巴動作來自 Mixamo；若要商業使用，請自行確認各素材原始授權。
- 姿勢辨識：Google MediaPipe Tasks Vision 與 Pose Landmarker 模型，Apache 2.0 授權。
- 巴恰塔與國標舞十支：沒有可用的免費真人錄製，動作是依各舞標準拍數規則以程式生成。
- 音樂有三種來源：
  - 內建伴奏：頁面即時合成（鼓組、貝斯、和弦，加上依舞種換音色的主旋律、每八小節的過門與殘響）。
  - 真實錄音：每種舞配一到兩首 Kevin MacLeod 的作品，播放時直接從 incompetech.com 線上串流，不放在本專案裡，所以需要連網。授權為 CC BY 4.0（https://creativecommons.org/licenses/by/4.0/），播放時頁面會顯示曲名與出處。曲目與速度列在 `web/music.js` 的 `TRACKS`。
  - 使用者加入的歌曲：只存在瀏覽器的 IndexedDB，不會上傳。
- YouTube 影片清單只是外部連結，影片版權屬於各上傳者。
