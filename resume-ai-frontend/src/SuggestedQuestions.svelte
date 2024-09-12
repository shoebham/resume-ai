<script>
  export let questions = [];
  export let onQuestionClick;
  export let isTyping;

  let clickedIndex = -1;

  function handleClick(question) {
    if (!isTyping) {
      onQuestionClick(question);
    }
  }
</script>

<div class="suggested-questions">
  {#each questions as question, index}
    <button 
      on:click={() => handleClick(question)} 
      disabled={isTyping}
    >
      {question}
    </button>
  {/each}
</div>

<style>
  .suggested-questions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;
  }

  button {
    background-color: #f0f0f0;
    border: none;
    border-radius: 16px;
    padding: 8px 16px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.3s ease, opacity 0.3s ease;
  }

  button:hover:not(:disabled) {
    background-color: #e0e0e0;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>