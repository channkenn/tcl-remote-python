function send(keyCode) {
  fetch(`/send_key/${keyCode}`);
}

function launch(appName) {
  fetch(`/launch/${appName}`);
}

function sendText() {
  const input = document.getElementById("tv_input");
  const text = input.value;
  if (text) {
    fetch(`/send_text?text=${encodeURIComponent(text)}`);
    input.value = "";
    input.blur();
  }
}
function deleteHistory(count) {
  fetch(`/delete_history/${count}`);
}
// 回数指定付きのチャンネル掃除
function cleanChannels(count) {
  fetch(`/clean_channels/${count}`);
}

// 既存のショート動画掃除も、最新の app.py に合わせておきます
function cleanShorts() {
  if (confirm("YouTubeホームのショート動画を一掃しますか？")) {
    fetch("/clean_shorts");
  }
}

// チャンネルIDとURLの定義（ここを編集するだけでボタンの飛び先を変えられます）
const channelList = {
  numberblocks: "https://www.youtube.com/@Numberblocks",
  zooming: "https://www.youtube.com/@zooming382",
  miwu: "https://www.youtube.com/@Miwu%E3%81%95%E3%82%93%E3%81%AE%E7%A7%91%E5%AD%A6%E3%81%AB%E3%81%BB%E3%82%93",
  denjiro: "https://www.youtube.com/@denjiroscience",
  animal: "https://www.youtube.com/@wakuwakutbs5820",
  jaxa: "https://www.youtube.com/@JAXA-HQ",
  factory: "https://www.youtube.com/@jstsciencechannel",
  music: "https://www.youtube.com/@SHIMAJIROCH",
  art: "https://www.youtube.com/@kokuyo",
  language: "https://www.youtube.com/@synapusyu",
  story: "https://www.youtube.com/@gakken_ehon",
  subs: "https://www.youtube.com/feed/subscriptions",
  later: "https://www.youtube.com/playlist?list=WL",
};

/**
 * 指定したタイプ（キー名）のURLをYouTube TVで開く
 */
function jumpTo(type) {
  const url = channelList[type];
  if (url) {
    // app.pyの /open_url エンドポイントを叩く
    fetch(`/open_url?url=${encodeURIComponent(url)}`)
      .then((response) => response.json())
      .then((data) => {
        if (!data.success) console.error("Jump failed:", data.error);
      });
  } else {
    console.error("Unknown channel type:", type);
  }
}

function cleanChannels(count) {
  fetch(`/clean_channels/${count}`);
}
