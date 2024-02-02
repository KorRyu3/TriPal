import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";

// WebSocketを開く
// ここら辺正直俺もよくわかってない
// FastAPIのdocsを参考に、とりあえずWebSocketを書く。
// https://fastapi.tiangolo.com/ja/advanced/websockets/

// const web_url = "tripal-ca.greenbay-9762fead.japaneast.azurecontainerapps.io";
const web_url = "127.0.0.1:8000";
const ws = new WebSocket("ws://" + web_url + "/chat");

// Websocketが接続されたときの処理
ws.onopen = function () {
  console.log("connected websocket main component");
};

// Websocketが切断されたときの処理
ws.onclose = function () {
  console.log("disconnected websocket main component");
  addMessage(
    "TriPalGPT",
    "ごめんね、接続が切れちゃったよ。リロードしてもう一度試してみてね。"
  );
};

// Websocketでエラーが発生したときの処理
ws.onerror = function (err) {
  console.error("Socket encountered error: ", err.message, "Closing socket");
  addMessage(
    "TriPalGPT",
    "ごめんね、エラーが発生しちゃったよ。リロードしてもう一度試してみてね。"
  );
  ws.close();
};

// 下までスクロールする
var scrollToBottom = () => {
  container.scrollTop = container.scrollHeight;
};

const chatArea = document.querySelector(".chat-area");
const typingArea = document.querySelector("#typing-area");
const userInputArea = document.querySelector(".user-inputArea");

// グローバルスコープまたは関数スコープの外部でカウンタを初期化
let detailCounter = 0;

// 入力エリアにsubmitイベントリスナーを追加
typingArea.addEventListener("submit", (event) => {
  // デフォルトのフォーム送信を防止
  event.preventDefault();
  // ユーザーの入力を取得
  const userInput = userInputArea.value;
  const safeInput = escapeHtml(userInput);
  userInputArea.value = "";
  addMessage("You", safeInput);

  // WebSocketにメッセージを送信
  ws.send(safeInput);

  // カウンタをインクリメント
  detailCounter++;

  // TriPalGPTからの返答を受け取る
  // TriPalGPT用の新しいdiv要素を作成
  const chatIOElement = document.createElement("div");
  chatIOElement.classList.add("chat", "ai-response");
  const chatDetailsElement = document.createElement("div");
  chatDetailsElement.className = "details";
  // TriPal_details_1という風にidの値が増えていく
  chatDetailsElement.id = "TriPal_details_" + detailCounter;

  // どんどん追加していくよ〜
  chatIOElement.appendChild(chatDetailsElement);
  chatArea.appendChild(chatIOElement);

  // 出力をぶち込む変数を定義
  let mdParse = "";
  ws.onmessage = function (event) {
    // event.dataをinnerHTMLに追加
    chatDetailsElement.innerHTML += event.data;
    // 退避用の変数に追加
    mdParse += event.data;
    if (event.data.includes("\n")) {
      // 今まで退避していたmdをパースし、innerHTMLで上書き
      chatDetailsElement.innerHTML = marked.parse(mdParse);
    }
  };

  // let streaming = "";
  // // メッセージを受け取り、chatDetailsElementに追加
  // ws.onmessage = function (event) {
  //   streaming += event.data;
  //   document.getElementById("TriPal_details_" + detailCounter).innerHTML =
  //     marked.parse(streaming);
  // streaming処理をしている中で、event.dataに\nがあるか判定
  //   if (event.data.includes("\n")) {
  //     document.getElementById("TriPal_details_" + detailCounter).innerHTML =
  //       marked.parse(chatDetailsElement.innerHTML + event.data);
  //   } else {
  //     chatDetailsElement.innerHTML += event.data;
  //   }
});

// メッセージをチャットエリアに追加する関数
function addMessage(sender, message) {
  // 送信者に基づいてクラス名を決定
  const classIOName = sender === "TriPalGPT" ? "ai-response" : "user-input";

  // おしゃべり用の新しいdiv要素を作成
  const chatIOElement = document.createElement("div");
  chatIOElement.classList.add("chat", classIOName);
  const chatDetailsElement = document.createElement("div");
  chatDetailsElement.className = "details";
  const messageP = document.createElement("p");
  messageP.innerHTML = message;

  // どんどん追加していくよ〜
  chatDetailsElement.appendChild(messageP);
  chatIOElement.appendChild(chatDetailsElement);
  chatArea.appendChild(chatIOElement);
}

// ユーザーからの入力をエスケープする処理
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
