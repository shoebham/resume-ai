<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { fade } from 'svelte/transition';
  import SuggestedQuestions from './SuggestedQuestions.svelte';
  let messages = [];
  let inputMessage = '';
  let chatContainer;
  let isTyping = false;
  let darkMode = writable(false);
  let suggestedQuestions = [];

  $: {
    if (typeof document !== 'undefined') {
      document.body.classList.toggle('dark', $darkMode);
    }
  }

  async function sendMessage() {
    if (!inputMessage.trim()) return;

    messages = [...messages, { text: inputMessage, sender: 'user' }];
    const userMessage = inputMessage;
    inputMessage = '';
    isTyping = true;
    suggestedQuestions = [];

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ text: userMessage })
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      isTyping = false;
      messages = [...messages, { text: data.response, sender: 'ai' }];
      suggestedQuestions = data.suggested_questions || [];
    } catch (error) {
      console.error('Error:', error);
      isTyping = false;
      messages = [...messages, { text: 'Sorry, an error occurred.', sender: 'ai' }];
      suggestedQuestions = [];
    }
  }

  function handleSuggestedQuestion(question) {
    inputMessage = question;
    sendMessage();
  }

  $: if (chatContainer) {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  onMount(() => {
    messages = [{ text: "Hello! I'm Shubham's Resume assistant. How can I help you?", sender: 'ai' }];
  });
</script>

<main class:dark={$darkMode}>
  <header class:dark={$darkMode}>
    <h1 class:dark={$darkMode}>Resume Chat</h1>
    <button class="toggle-button" on:click={() => darkMode.update(n => !n)}>
      {#if $darkMode}
        <span style="color: white;">Light Mode</span>
      {:else}
        <span class="dark-mode-icon">Dark Mode</span>
      {/if}
    </button>
  </header>
  
  <div class="chat-container" class:dark={$darkMode} bind:this={chatContainer}>
    {#each messages as message (message)}
      <div class="message {message.sender}" in:fade={{ duration: 150 }}>
        <p class:dark={$darkMode}>{message.text}</p>
      </div>
    {/each}
    {#if isTyping}
      <div class="message ai typing" in:fade={{ duration: 150 }}>
        <div class="typing-indicator" class:dark={$darkMode}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    {/if}
<SuggestedQuestions questions={suggestedQuestions} onQuestionClick={handleSuggestedQuestion} {isTyping} />
  </div>
  
  <div class="input-container" class:dark={$darkMode}>
    <input
      type="text"
      bind:value={inputMessage}
      on:keydown={(e) => e.key === 'Enter' && sendMessage()}
      placeholder="Type your message..."
      class:dark={$darkMode}
    />
    <button on:click={sendMessage} class:dark={$darkMode}>Send</button>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Roboto', 'Segoe UI', 'Arial', sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    color: #333;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    transition: background 0.3s ease, color 0.3s ease;
    line-height: 1.6;
  }

  :global(body.dark) {
    background: linear-gradient(135deg, #2c3e50 0%, #1a1a1a 100%);
    color: #ffffff;
  }

  main {
    display: flex;
    flex-direction: column;
    width: 90%;
    max-width: 800px;
    height: 90vh;
    background-color: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    overflow: hidden;
    color: #333333;
    transition: all 0.3s ease;
    transform: translateY(0);
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1), 0 0 40px rgba(0, 0, 0, 0.1);
    font-size: 16px;
    letter-spacing: 0.3px;
  }

  main.dark {
    background-color: rgba(30, 30, 30, 0.9);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    color: #ffffff;
  }

  header {
    background-color: #f1f1f1;
    padding: 20px;
    text-align: center;
    position: relative;
  }

  header.dark {
    background-color: #333;
  }

  .back-button {
    position: absolute;
    left: 20px;
    top: 20px;
    background: none;
    border: none;
    color: #333;
    font-size: 24px;
    cursor: pointer;
  }

  .back-button.dark {
    color: #ffffff;
  }

  h1 {
    font-family: 'Poppins', 'Roboto', 'Segoe UI', sans-serif;
    font-weight: 600;
    font-size: 28px;
    margin: 0;
    color: #333;
    margin-bottom: 10px;
  }

  h1.dark {
    color: #ffffff;
  }

  p {
    margin: 10px 0 0;
    font-size: 14px;
  }


  .username {
    color: #007bff;
  }

  .username.dark {
    color: #1e90ff;
  }

  .toggle-button {
    position: absolute;
    right: 20px;
    top: 20px;
    background: none;
    border: none;
    color: #333;
    font-size: 16px;
    cursor: pointer;
  }

  .toggle-button.dark {
    color: #ffffff;
  }

  .chat-container {
    flex-grow: 1;
    overflow-y: auto;
    padding: 20px;
    background-color: rgba(249, 249, 249, 0.8);
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 20px;
    transition: background-color 0.3s ease;
  }

  .chat-container.dark {
    background-color: rgba(46, 46, 46, 0.8);
    box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
  }


  .message {
    max-width: 80%;
    margin-bottom: 15px;
    padding: 8px;
    border-radius: 18px;
    line-height: 1.5;
    word-wrap: break-word;
    opacity: 0;
    transform: translateY(20px);
    animation: fadeIn 0.3s ease forwards;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    font-size: 15px;
  }

  @keyframes fadeIn {
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .message.user {
    background-color: #007bff;
    color: #ffffff;
    align-self: flex-end;
    margin-left: auto;
    border-bottom-right-radius: 4px;
  }

  .message.user.dark {
    background-color: #1e90ff;
  }

  .message.ai {
    background-color: #f0f0f0;
    color: #333333;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
  }

  .message.ai.dark {
    background-color: #2a2a2a;
    color: #ffffff;
  }

  .input-container {
    display: flex;
    padding: 20px;
    background-color: #f1f1f1;
    border-radius: 0 0 10px 10px;
    transition: background-color 0.3s ease;
  }

  .input-container:focus-within {
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  }

  .input-container.dark {
    background-color: #333;
  }

  .input-container.dark:focus-within {
    box-shadow: 0 -2px 10px rgba(255, 255, 255, 0.1);
  }

  input {
    flex-grow: 1;
    padding: 10px 15px;
    border: 1px solid #ccc;
    border-radius: 25px;
    background-color: #ffffff;
    color: #333;
    font-size: 15px;
    font-family: 'Roboto', 'Segoe UI', 'Arial', sans-serif;
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
  }

  input.dark {
    background-color: #444;
    color: #ffffff;
    border: 1px solid #555;
  }

  input::placeholder {
    color: #999;
    transition: color 0.3s ease;
  }

  input.dark::placeholder {
    color: #cccccc;
  }

  button {
    margin-left: 10px;
    padding: 10px 20px;
    border: none;
    border-radius: 25px;
    background-color: #007bff;
    color: #ffffff;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    font-family: 'Roboto', 'Segoe UI', 'Arial', sans-serif;
    font-weight: 500;
    letter-spacing: 0.5px;
  }

  button.dark {
    background-color: #1e90ff;
  }

  button:hover {
    background-color: #0056b3;
  }

  button.dark:hover {
    background-color: #1c7ed6;
  }

  .typing-indicator {
    display: flex;
    align-items: center;
  }

  .typing-indicator span {
    height: 8px;
    width: 8px;
    margin: 0 2px;
    background-color: #999;
    display: block;
    border-radius: 50%;
    opacity: 0.4;
    animation: 1s blink infinite;
  }

  .typing-indicator.dark span {
    background-color: #cccccc;
  }

  @keyframes blink {
    50% {
      opacity: 1;
    }
  }
</style>