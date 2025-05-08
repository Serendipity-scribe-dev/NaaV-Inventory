// GPT code
document.addEventListener('DOMContentLoaded', () => {
    const userMessageInput = document.getElementById('user-prompt');
    const sendButton = document.getElementById('send-button');
    const chatHistory = document.getElementById('chat-history');

    const userLogoSVG = `
    <svg class="chat-svg" height="30px" width="30px" fill="#000000" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"> 
    <g>
        <path class="st0" d="M159.131,169.721c5.635,58.338,43.367,96.867,96.871,96.867c53.502,0,91.23-38.53,96.867-96.867l7.988-63.029 C365.812,44.768,315.281,0,256.002,0c-59.281,0-109.812,44.768-104.86,106.692L159.131,169.721z"/>
        <path class="st0" d="M463.213,422.569l-3.824-24.35c-3.203-20.417-16.035-38.042-34.475-47.361l-80.473-40.693 c-2.519-1.274-4.57-3.194-6.289-5.338c-23.297,24.632-51.6,39.12-82.15,39.12c-30.549,0-58.856-14.488-82.152-39.12 c-1.719,2.144-3.77,4.064-6.289,5.338l-80.472,40.693c-18.442,9.319-31.272,26.944-34.475,47.361l-3.826,24.35 c-1.363,8.692,0.436,21.448,8.222,27.825C67.42,458.907,105.875,512,256.002,512c150.125,0,188.578-53.093,198.988-61.606 C462.779,444.017,464.576,431.261,463.213,422.569z"/>
    </g>
    </svg>`;

    const botLogoSVG = `
    <svg width="30px" height="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"> 
        <path d="M9 15C8.44771 15 8 15.4477 8 16C8 16.5523 8.44771 17 9 17C9.55229 17 10 16.5523 10 16C10 15.4477 9.55229 15 9 15Z" fill="#0F0F0F"/>
        <path d="M14 16C14 15.4477 14.4477 15 15 15C15.5523 15 16 15.4477 16 16C16 16.5523 15.5523 17 15 17C14.4477 17 14 16.5523 14 16Z" fill="#0F0F0F"/>
        <path fill-rule="evenodd" clip-rule="evenodd" d="M12 1C10.8954 1 10 1.89543 10 3C10 3.74028 10.4022 4.38663 11 4.73244V7H6C4.34315 7 3 8.34315 3 10V20C3 21.6569 4.34315 23 6 23H18C19.6569 23 21 21.6569 21 20V10C21 8.34315 19.6569 7 18 7H13V4.73244C13.5978 4.38663 14 3.74028 14 3C14 1.89543 13.1046 1 12 1ZM5 10C5 9.44772 5.44772 9 6 9H7.38197L8.82918 11.8944C9.16796 12.572 9.86049 13 10.618 13H13.382C14.1395 13 14.832 12.572 15.1708 11.8944L16.618 9H18C18.5523 9 19 9.44772 19 10V20C19 20.5523 18.5523 21 18 21H6C5.44772 21 5 20.5523 5 20V10ZM13.382 11L14.382 9H9.61803L10.618 11H13.382Z" fill="#0F0F0F"/>
        <path d="M1 14C0.447715 14 0 14.4477 0 15V17C0 17.5523 0.447715 18 1 18C1.55228 18 2 17.5523 2 17V15C2 14.4477 1.55228 14 1 14Z" fill="#0F0F0F"/>
        <path d="M22 15C22 14.4477 22.4477 14 23 14C23.5523 14 24 14.4477 24 15V17C24 17.5523 23.5523 18 23 18C22.4477 18 22 17.5523 22 17V15Z" fill="#0F0F0F"/>
    </svg>`;
    

    function addUserMessage(message) {
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'chat-user';

        const userTextDiv = document.createElement('div');
        userTextDiv.className = 'chat-user-text message-content user';
        userTextDiv.textContent = message;

        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = new Date().toLocaleTimeString('en-IN', {
            hour: 'numeric',
            minute: 'numeric',
            hour12: true
        });

        const chatUserLogo = document.createElement('div');
        chatUserLogo.className = 'chat-user-logo';
        chatUserLogo.innerHTML = `<h4>User</h4>${userLogoSVG}`;

        userTextDiv.appendChild(timestampDiv);
        userMessageDiv.appendChild(chatUserLogo);
        userMessageDiv.appendChild(userTextDiv);
        chatHistory.appendChild(userMessageDiv);
        scrollToBottom();
    }

    function addBotMessage(message) {
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'chat-bot';

        const botTextDiv = document.createElement('div');
        botTextDiv.className = 'chat-bot-text message-content bot';
        botTextDiv.textContent = message;

        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = new Date().toLocaleTimeString('en-IN', {
            hour: 'numeric',
            minute: 'numeric',
            hour12: true
        });

        const chatBotLogo = document.createElement('div');
        chatBotLogo.className = 'chat-bot-logo';
        chatBotLogo.innerHTML = `${botLogoSVG}<h4>MediBot</h4>`;

        botTextDiv.appendChild(timestampDiv);
        botMessageDiv.appendChild(chatBotLogo);
        botMessageDiv.appendChild(botTextDiv);
        chatHistory.appendChild(botMessageDiv);
        scrollToBottom();
    }

    // New part
    function addBotMessageHTML(message) {
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'chat-bot';

        const botTextDiv = document.createElement('div');
        botTextDiv.className = 'chat-bot-text message-content bot';
        botTextDiv.innerHTML = message;

        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = new Date().toLocaleTimeString('en-IN', {
            hour: 'numeric',
            minute: 'numeric',
            hour12: true
        });

        const chatBotLogo = document.createElement('div');
        chatBotLogo.className = 'chat-bot-logo';
        chatBotLogo.innerHTML = `${botLogoSVG}<h4>MediBot</h4>`;

        botTextDiv.appendChild(timestampDiv);
        botMessageDiv.appendChild(chatBotLogo);
        botMessageDiv.appendChild(botTextDiv);
        chatHistory.appendChild(botMessageDiv);
        scrollToBottom();
    }
    // 

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    userMessageInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendButton.click();
        }
    });

    // 📌Sending the Prompt entered by user to the flask backend
    sendButton.addEventListener('click', async () => {
        const data = userMessageInput.value; // Corrected from userInput.value to userMessageInput.value
        addUserMessage(data);
        userMessageInput.value = ""
        const response = await fetch('/chatbot/', {
            method: 'POST',
            body: JSON.stringify({ data: data }),
            headers: { 'Content-Type': 'application/json' }
        });
        // addBotMessageHTML(htmlCode)

        if (response.ok) {
            const responseData = await response.json(); // Parse JSON response from the server
            // addBotMessage(responseData.response); // Correctly add the bot message

            var cleanString = responseData.response
            var cleanString = cleanString.replace(/```html/g, '').replace(/```/g, '').replace(/\n/g, ''); 
            addBotMessageHTML(cleanString)
            console.log("Data sent successfully!");
        } else {
            console.error("Error sending data:", response.statusText);
        }
    });
});
