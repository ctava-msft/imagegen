document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("message-form").addEventListener("submit", async function (event) {
            event.preventDefault(); // Prevent the default form submission behavior

            const prompt = document.getElementById("prompt").value; // Get the value from the textarea

            // Check if the prompt is not empty
            if (!prompt.trim()) {
                alert("Please enter a prompt");
                return;
            }

            try {
                const response = await fetch(
                    "{{ url_for('app.generate_response', session_id=session_id) }}",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            user_input: prompt, // Send prompt as part of JSON body
                        }),
                    }
                );

                const data = await response.json();
                console.log(data.response);

                // Append the new message to the chat window
                const chatSession = document.getElementById("chat-session");
                const userMessage = document.createElement("li");
                userMessage.className = "message user";
                userMessage.innerHTML = `<div class="content"><p>${prompt}</p></div>`;
                chatSession.appendChild(userMessage);

                const assistantMessage = document.createElement("li");
                assistantMessage.className = "message assistant";
                assistantMessage.innerHTML = `<div class="content"><p>${data.response}</p></div>`;
                chatSession.appendChild(assistantMessage);

                // Clear the input field
                document.getElementById("prompt").value = "";
            } catch (error) {
                console.error('Error:', error);
            }
        });
});