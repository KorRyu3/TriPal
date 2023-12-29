const chatArea = document.getElementsByClassName('chat-area')[0];
const typingArea = document.getElementById('typing-area');
const userInputArea = document.getElementsByClassName('user-inputArea')[0];

typingArea.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = userInputArea.value;
  const formData = new FormData(typingArea);

  userInputArea.value = '';
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

  let classIOName = "user-input"
  if (sender == "TriPalGPT") {
    classIOName = "ai-response"
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
  chatArea.appendChild(chatIOElement);

}