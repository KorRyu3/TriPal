import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
// ------------------------------
// https://fastapi.tiangolo.com/ja/advanced/websockets/

// フロントエンド開発用兼デプロイ用WebSocket
// PRするときは、下のデバッグ用をコメントアウトし、こっちを有効化してください。
const web_url = "tripal-ca.greenbay-9762fead.japaneast.azurecontainerapps.io";
const ws = new WebSocket("wss://" + web_url + "/chat");

// バックエンド開発用WebSocket
// フロントエンド開発するなら、こっちはコメントアウトしたままで大丈夫
// PRする時は、コメントアウトすること
// const web_url = "127.0.0.1:8000";
// const ws = new WebSocket("ws://" + web_url + "/chat");

// ------------------------------
// WebSocketのイベントハンドラを設定
ws.onopen = function () {
  console.log("connected websocket main component");
};

ws.onclose = function () {
  console.log("disconnected websocket main component");
  addMessage(
    "TriPalGPT",
    "ごめんね、接続が切れちゃったよ。リロードしてもう一度試してみてね。"
  );
};

ws.onerror = function (err) {
  console.error("Socket encountered error: ", err.message, "Closing socket");
  addMessage(
    "TriPalGPT",
    "ごめんね、エラーが発生しちゃったよ。リロードしてもう一度試してみてね。"
  );
  ws.close();
};

// DOM要素を取得
const chatArea = document.querySelector(".chat-area");
const typingArea = document.querySelector("#typing-area");
const userInputArea = document.querySelector(".user-inputArea");
const sendButton = document.getElementById("submit");

// メッセージ詳細のカウンタを初期化
let detailCounter = 0;

// typingAreaにsubmitイベントリスナーを追加
typingArea.addEventListener("submit", (event) => {
  // フォームのデフォルトの送信動作をキャンセル
  event.preventDefault();

  // ユーザーの入力を取得し、HTMLエスケープ処理を行う
  const userInput = userInputArea.value;
  const safeInput = escapeHtml(userInput);

  // 入力エリアをクリア
  userInputArea.value = "";

  // ユーザーのメッセージをチャットエリアに追加
  addMessage("You", safeInput);

  // メッセージをWebSocketを通じてサーバーに送信
  ws.send(safeInput);

  // メッセージ詳細のカウンタをインクリメント
  detailCounter++;

  // メッセージを表示するためのdiv要素を作成し、クラスとIDを設定
  const chatIOElement = document.createElement("div");
  chatIOElement.classList.add("chat", "ai-response");
  const chatDetailsElement = document.createElement("div");
  chatDetailsElement.className = "details";
  chatDetailsElement.id = "TriPal_details_" + detailCounter;

  // chatIOElementの子要素としてchatDetailsElementを追加
  chatIOElement.appendChild(chatDetailsElement);

  // chatAreaの子要素としてchatIOElementを追加
  chatArea.appendChild(chatIOElement);

  // Markdownパース用の変数を初期化
  let mdParse = "";

  // WebSocketからメッセージを受信したときの処理
  ws.onmessage = function (event) {
    // 受信したメッセージをchatDetailsElementに追加
    chatDetailsElement.innerHTML += event.data;

    // Markdownパース用の変数に受信したメッセージを追加
    mdParse += event.data;

    // 受信したメッセージに改行が含まれている場合、Markdownパースを行う
    if (event.data.includes("\n")) {
      chatDetailsElement.innerHTML = marked.parse(mdParse);
    }

    // 新しいメッセージが追加されたので、handleNewMessage関数を呼び出す
    handleNewMessage();
  };
});

// メッセージをチャットエリアに追加する関数
function addMessage(sender, message) {
  // senderが"TriPalGPT"なら"ai-response"、それ以外なら"user-input"をclassIONameに設定
  const classIOName = sender === "TriPalGPT" ? "ai-response" : "user-input";

  // メッセージを表示するためのdiv要素を作成
  const chatIOElement = document.createElement("div");
  // 作成したdiv要素に"chat"とclassIONameをクラスとして追加
  chatIOElement.classList.add("chat", classIOName);

  // メッセージ詳細を表示するためのdiv要素を作成
  const chatDetailsElement = document.createElement("div");
  // 作成したdiv要素に"details"をクラスとして設定
  chatDetailsElement.className = "details";

  // メッセージ本文を表示するためのp要素を作成
  const messageP = document.createElement("p");
  // 作成したp要素のinnerHTMLにメッセージを設定
  messageP.innerHTML = message;

  // chatDetailsElementの子要素としてmessagePを追加
  chatDetailsElement.appendChild(messageP);
  // chatIOElementの子要素としてchatDetailsElementを追加
  chatIOElement.appendChild(chatDetailsElement);
  // chatAreaの子要素としてchatIOElementを追加
  chatArea.appendChild(chatIOElement);

  // 新しいメッセージが追加されたので、handleNewMessage関数を呼び出す
  handleNewMessage();
}

// ユーザーがスクロールしたかどうかを追跡するフラグ
let userScrolled = false;

// スクロールイベントリスナーを追加
// ユーザーがスクロールした場合、userScrolledフラグを更新
document.getElementById("chatBox").addEventListener("scroll", function () {
  userScrolled = this.scrollTop + this.clientHeight + 1 < this.scrollHeight;
});

// 新しいメッセージが追加された際に自動スクロールする関数
function handleNewMessage() {
  // ユーザーがスクロールしていない場合のみ自動スクロールを実行
  if (!userScrolled) {
    // チャットコンテナのDOM要素を取得
    const chatContainer = document.getElementById("chatBox");
    // チャットコンテナの最後のメッセージ要素を取得
    const lastMessage = chatContainer.lastElementChild;

    // 最後のメッセージが存在する場合のみ自動スクロールを実行
    if (lastMessage) {
      // 最後のメッセージの位置情報を取得
      const lastMessageRect = lastMessage.getBoundingClientRect();
      // チャットコンテナの高さを取得
      const containerHeight = chatContainer.clientHeight;
      // チャットコンテナの現在のスクロール位置を取得
      const scrollTop = chatContainer.scrollTop;

      // 最後のメッセージがチャットコンテナの表示領域を超えている場合、そのメッセージが見えるようにスクロール
      if (lastMessageRect.bottom > containerHeight) {
        chatContainer.scrollTo({
          top: scrollTop + lastMessageRect.bottom - containerHeight,
          behavior: "smooth",
        });
      }
    }
  }
}

// 入力をロック/アンロックする関数
function lockInput() {
  sendButton.disabled = true;
}

function unlockInput() {
  sendButton.disabled = false;
}

// ユーザーからの入力をエスケープする関数
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
