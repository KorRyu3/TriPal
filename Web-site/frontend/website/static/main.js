const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const userChat = document.getElementById("user-chat");

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = userChat.value;
  const formData = new FormData(chatForm);

  userChat.value = "";
  addMessage("You", message);

  fetch("/chat", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      const message = data.response;
      addMessage("TriPalGPT", message);
    })
    .catch((error) => {
      console.error(error);
    });
});

function addMessage(sender, message) {
  const messageElement = document.createElement("div");
  messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
  if (sender == "TriPalGPT") messageElement.innerHTML += "<br>";
  chatLog.appendChild(messageElement);
}
