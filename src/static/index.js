const chatArea = document.querySelector(".chat-area");
const typingArea = document.querySelector("#typing-area");
const userInputArea = document.querySelector(".user-inputArea");

// 入力エリアにsubmitイベントリスナーを追加
typingArea.addEventListener("submit", (event) => {
  // デフォルトのフォーム送信を防止
  event.preventDefault();
  // ユーザーの入力を取得
  const message = userInputArea.value;
  userInputArea.value = "";

  // フォームデータを作成
  const formData = new FormData(typingArea);
  addMessage("You", message);

  // サーバーにPOSTリクエストを送信
  fetch("/chat", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json()) // レスポンスをJSONに変換
    .then((data) => {
      // レスポンスからメッセージを取得
      const message = data.response;
      // AIのメッセージをチャットエリアに追加
      addMessage("TriPalGPT", message);
    })
    .catch((error) => {
      // エラーをコンソールに出力
      console.error(error);
      // エラーメッセージをチャットエリアに追加
      addMessage("System", `Error: ${error.message}`);
    });
});

// ストリーミング機能を使って、サーバーからのメッセージを受信
function sendQuestionForStreaming() {
  var userInput = document.querySelector(".user-inputArea").value;
  displayUserInput(userInput);
  var streamUrl =
    "http://0.0.0.0:8000/stream?user_chat=" + encodeURIComponent(userInput);
  document.querySelector(".user-inputArea").value = "";

  var eventSource = new EventSource(streamUrl);

  var responseDiv = createNewChatBox();
  let isFirstMessage = true;
  let currentMessage = "";

  eventSource.onmessage = function (event) {
    var data = JSON.parse(event.data);

    if (isFirstMessage && data.message === "") {
      isFirstMessage = false;
      return;
    }
    if (data.message === "") {
      eventSource.close();
    } else {
      currentMessage += data.message;
      updateChatBox(responseDiv, currentMessage);
    }
  };

  eventSource.onerror = function (error) {
    console.error("EventSource failed:", error);
    eventSource.close();
  };
}

document
  .querySelector("#typing-area")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    if (eventSource) {
      eventSource.close();
    }
  });

// const messagesDiv = document.getElementById("chatBox");

// const eventSource = new EventSource("/chat");
// eventSource.onmessage = function (event) {
//   const data = event.data;
//   messagesDiv.innerHTML += data;
// };
// eventSource.onerror = function (event) {
//   console.error("Connection error:", event);
//   eventSource.close();
// };

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
