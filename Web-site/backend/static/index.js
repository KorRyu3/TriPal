const chatBox = document.getElementsByClassName('chat-box')[0];
const typingArea = document.getElementById('typing-area');
const userChat = document.getElementsByClassName('user-chat')[0];

typingArea.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = userChat.value;
  const formData = new FormData(typingArea);

  userChat.value = '';
  addMessage('You', message);

  
  fetch('/chat', {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      const message = data.response;
      addMessage('TriPalGPT', message);
  })
  .catch(error => {
      console.error(error);
  });
});

function addMessage(sender, message) {

  // I=user, O=LLM
  
  let classIOName = "outgoing"
  if (sender == "TriPalGPT") {
    classIOName = "incoming"
  }
  
  const chatIOElement = document.createElement('div');
  chatIOElement.classList.add("chat", classIOName);

  const chatDetailsElement = document.createElement('div');
  chatDetailsElement.className = "details";

  if (sender == "You") {
    const userP = document.createElement('p');
    userP.innerHTML = `${message}`;
    chatDetailsElement.appendChild(userP);
  }
  else if (sender == "TriPalGPT") {
    const gptP = document.createElement('p');
    gptP.innerHTML = `${message}`;
    chatDetailsElement.appendChild(gptP);

  }

  chatIOElement.appendChild(chatDetailsElement);
  chatBox.appendChild(chatIOElement);
  
}
