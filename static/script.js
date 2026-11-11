// =====================================================
// PARENT TEACHER BRIDGE
// SHARED JAVASCRIPT
// =====================================================


// =====================================================
// HOME PAGE IMAGE SLIDER
// =====================================================

let slideIndex = 0;


function showSlide(index) {

    const slides =
        document.querySelectorAll(".slide");

    const dots =
        document.querySelectorAll(".dot");


    if (slides.length === 0) {
        return;
    }


    if (index >= slides.length) {
        slideIndex = 0;
    }


    if (index < 0) {
        slideIndex = slides.length - 1;
    }


    slides.forEach(function (slide) {

        slide.classList.remove("active");

    });


    dots.forEach(function (dot) {

        dot.classList.remove("active-dot");

    });


    slides[slideIndex].classList.add("active");


    if (dots[slideIndex]) {

        dots[slideIndex].classList.add("active-dot");

    }

}


function changeSlide(direction) {

    slideIndex += direction;

    showSlide(slideIndex);

}


function currentSlide(index) {

    slideIndex = index;

    showSlide(slideIndex);

}


// Automatic slider

setInterval(function () {

    if (document.querySelector(".slide")) {

        slideIndex++;

        showSlide(slideIndex);

    }

}, 5000);


// =====================================================
// LANGUAGE
// =====================================================

function setLanguage(language) {

    localStorage.setItem(
        "language",
        language
    );

    applyLanguage(language);

}


function applyLanguage(language) {

    const heroTitle =
        document.querySelector(
            ".hero-overlay h1"
        );

    const heroText =
        document.querySelector(
            ".hero-overlay p"
        );


    if (!heroTitle || !heroText) {
        return;
    }


    const translations = {

        english: {

            title:
                "Parent Teacher Bridge",

            text:
                "Connecting parents, teachers and schools through technology."

        },


        hindi: {

            title:
                "पेरेंट टीचर ब्रिज",

            text:
                "तकनीक के माध्यम से माता-पिता, शिक्षकों और विद्यालयों को जोड़ना।"

        },


        odia: {

            title:
                "ପ୍ୟାରେଣ୍ଟ ଟିଚର ବ୍ରିଜ୍",

            text:
                "ପ୍ରଯୁକ୍ତି ମାଧ୍ୟମରେ ଅଭିଭାବକ, ଶିକ୍ଷକ ଏବଂ ବିଦ୍ୟାଳୟକୁ ସଂଯୋଗ କରିବା।"

        }

    };


    if (translations[language]) {

        heroTitle.innerText =
            translations[language].title;

        heroText.innerText =
            translations[language].text;

    }

}


// Load saved language

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const savedLanguage =
            localStorage.getItem(
                "language"
            ) || "english";


        const selector =
            document.querySelector(
                ".language-select"
            );


        if (selector) {

            selector.value =
                savedLanguage;

        }


        applyLanguage(
            savedLanguage
        );


        showSlide(slideIndex);

    }
);


// =====================================================
// PARENT DASHBOARD SIDEBAR
// =====================================================

function toggleParentSidebar() {

    const sidebar =
        document.getElementById(
            "parentSidebar"
        );


    if (sidebar) {

        sidebar.classList.toggle(
            "active"
        );

    }

}


// =====================================================
// TEACHER DASHBOARD SIDEBAR
// =====================================================

function toggleTeacherSidebar() {

    const sidebar =
        document.getElementById(
            "teacherSidebar"
        );


    if (sidebar) {

        sidebar.classList.toggle(
            "active"
        );

    }

}


// =====================================================
// ADMIN DASHBOARD SIDEBAR
// =====================================================

function toggleAdminSidebar() {

    const sidebar =
        document.getElementById(
            "adminSidebar"
        );

    const overlay =
        document.getElementById(
            "adminSidebarOverlay"
        );


    if (!sidebar) {
        return;
    }


    sidebar.classList.toggle(
        "active"
    );


    if (overlay) {

        overlay.classList.toggle(
            "active"
        );

    }

}


// =====================================================
// CLOSE ADMIN SIDEBAR
// =====================================================

function closeAdminSidebar() {

    const sidebar =
        document.getElementById(
            "adminSidebar"
        );

    const overlay =
        document.getElementById(
            "adminSidebarOverlay"
        );


    if (sidebar) {

        sidebar.classList.remove(
            "active"
        );

    }


    if (overlay) {

        overlay.classList.remove(
            "active"
        );

    }

}


// =====================================================
// CLOSE SIDEBAR WHEN CLICKING OUTSIDE
// =====================================================

document.addEventListener(
    "click",
    function (event) {

        const parentSidebar =
            document.getElementById(
                "parentSidebar"
            );

        const teacherSidebar =
            document.getElementById(
                "teacherSidebar"
            );

        const adminSidebar =
            document.getElementById(
                "adminSidebar"
            );


        const parentButton =
            document.querySelector(
                ".settings-button"
            );

        const teacherButton =
            document.querySelector(
                ".settings-btn"
            );

        const adminButton =
            document.querySelector(
                ".admin-settings-button"
            );


        // -------------------------------------------------
        // PARENT SIDEBAR
        // -------------------------------------------------

        if (
            parentSidebar &&
            parentSidebar.classList.contains("active") &&
            !parentSidebar.contains(event.target) &&
            !(
                parentButton &&
                parentButton.contains(event.target)
            )
        ) {

            parentSidebar.classList.remove(
                "active"
            );

        }


        // -------------------------------------------------
        // TEACHER SIDEBAR
        // -------------------------------------------------

        if (
            teacherSidebar &&
            teacherSidebar.classList.contains("active") &&
            !teacherSidebar.contains(event.target) &&
            !(
                teacherButton &&
                teacherButton.contains(event.target)
            )
        ) {

            teacherSidebar.classList.remove(
                "active"
            );

        }


        // -------------------------------------------------
        // ADMIN SIDEBAR
        // -------------------------------------------------

        if (
            adminSidebar &&
            adminSidebar.classList.contains("active") &&
            !adminSidebar.contains(event.target) &&
            !(
                adminButton &&
                adminButton.contains(event.target)
            )
        ) {

            closeAdminSidebar();

        }

    }
);


// =====================================================
// PARENT / TEACHER SIDEBAR CLOSE BUTTONS
// =====================================================

document.addEventListener(
    "click",
    function (event) {

        if (
            event.target.classList.contains(
                "close-sidebar"
            )
        ) {

            const parentSidebar =
                document.getElementById(
                    "parentSidebar"
                );

            const teacherSidebar =
                document.getElementById(
                    "teacherSidebar"
                );


            if (parentSidebar) {

                parentSidebar.classList.remove(
                    "active"
                );

            }


            if (teacherSidebar) {

                teacherSidebar.classList.remove(
                    "active"
                );

            }

        }

    }
);


// =====================================================
// ADMIN SIDEBAR CLOSE BUTTON
// =====================================================

document.addEventListener(
    "click",
    function (event) {

        if (
            event.target.classList.contains(
                "admin-close-sidebar"
            )
        ) {

            closeAdminSidebar();

        }

    }
);


// =====================================================
// CLOSE ALL SIDEbars WITH ESC KEY
// =====================================================

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key !== "Escape") {
            return;
        }


        const parentSidebar =
            document.getElementById(
                "parentSidebar"
            );

        const teacherSidebar =
            document.getElementById(
                "teacherSidebar"
            );


        if (parentSidebar) {

            parentSidebar.classList.remove(
                "active"
            );

        }


        if (teacherSidebar) {

            teacherSidebar.classList.remove(
                "active"
            );

        }


        closeAdminSidebar();

    }
);


// =====================================================
// PARENT TEACHER BRIDGE
// VOICE MESSAGE / CHAT
// =====================================================


// =====================================================
// CHAT DATA
// =====================================================

const chatData = {

    "Rahul Kumar": {

        status:
            "Parent • Online",

        messages: [

            {
                type: "sent",

                text:
                    "Hello! How is Rahul doing with his mathematics homework?",

                time:
                    "10:25 AM"
            },

            {
                type: "received",

                text:
                    "Hello teacher. He is doing well and completed most of it.",

                time:
                    "10:28 AM"
            },

            {
                type: "received",

                voice: true,

                duration:
                    "0:18",

                time:
                    "10:30 AM"
            },

            {
                type: "sent",

                text:
                    "That's great. Please make sure he revises the multiplication chapter before Friday.",

                time:
                    "10:32 AM"
            }

        ]

    },


    "Priya Das": {

        status:
            "Parent • Online",

        messages: [

            {
                type: "sent",

                text:
                    "Good morning. Please check Priya's homework.",

                time:
                    "09:40 AM"
            },

            {
                type: "received",

                text:
                    "I will check it today, teacher.",

                time:
                    "09:45 AM"
            }

        ]

    },


    "Rohan Mishra": {

        status:
            "Parent • Offline",

        messages: [

            {
                type: "sent",

                text:
                    "Rohan needs some additional practice in mathematics.",

                time:
                    "Yesterday"
            },

            {
                type: "received",

                voice: true,

                duration:
                    "0:24",

                time:
                    "Yesterday"
            }

        ]

    },


    "Anjali Sahoo": {

        status:
            "Parent • Offline",

        messages: [

            {
                type: "received",

                text:
                    "Good morning teacher.",

                time:
                    "Yesterday"
            },

            {
                type: "sent",

                text:
                    "Good morning. Anjali is doing very well in class.",

                time:
                    "Yesterday"
            }

        ]

    }

};


// =====================================================
// CURRENT CHAT
// =====================================================

let currentChat =
    "Rahul Kumar";


// =====================================================
// OPEN CONVERSATION
// =====================================================

function openConversation(name) {

    currentChat = name;


    const userName =
        document.getElementById(
            "chatUserName"
        );

    const userStatus =
        document.getElementById(
            "chatUserStatus"
        );


    if (userName) {

        userName.textContent =
            name;

    }


    if (userStatus) {

        userStatus.textContent =
            chatData[name]?.status ||
            "Parent";

    }


    document.querySelectorAll(
        ".conversation"
    ).forEach(function (chat) {

        chat.classList.remove(
            "active"
        );

    });


    document.querySelectorAll(
        ".conversation"
    ).forEach(function (chat) {

        if (
            chat.innerText.includes(name)
        ) {

            chat.classList.add(
                "active"
            );

        }

    });


    renderMessages(name);


    closeChatSidebar();

}


// =====================================================
// DISPLAY MESSAGES
// =====================================================

function renderMessages(name) {

    const messagesArea =
        document.getElementById(
            "messagesArea"
        );


    if (!messagesArea) {
        return;
    }


    const conversation =
        chatData[name];


    if (!conversation) {
        return;
    }


    messagesArea.innerHTML = "";


    const date =
        document.createElement(
            "div"
        );


    date.className =
        "chat-date";


    date.textContent =
        "Today";


    messagesArea.appendChild(date);


    conversation.messages.forEach(
        function (message) {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "message-row " +
                message.type;


            if (message.voice) {

                row.innerHTML = `

                    <div>

                        <div class="voice-message">

                            <button
                                class="play-voice"
                                onclick="playVoiceMessage(this)">

                                ▶

                            </button>

                            <div class="voice-wave">

                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>

                            </div>

                            <span class="voice-duration">

                                ${message.duration}

                            </span>

                        </div>

                        <span class="message-time">

                            ${message.time}

                        </span>

                    </div>

                `;

            }


            else {

                row.innerHTML = `

                    <div class="message-bubble">

                        <p>
                            ${escapeHTML(
                                message.text
                            )}
                        </p>

                        <span class="message-time">

                            ${message.time}

                        </span>

                    </div>

                `;

            }


            messagesArea.appendChild(
                row
            );

        }
    );


    messagesArea.scrollTop =
        messagesArea.scrollHeight;

}


// =====================================================
// SEND MESSAGE
// =====================================================

function sendMessage() {

    const input =
        document.getElementById(
            "messageInput"
        );


    if (!input) {
        return;
    }


    const text =
        input.value.trim();


    if (text === "") {
        return;
    }


    if (!chatData[currentChat]) {

        chatData[currentChat] = {

            status:
                "Parent",

            messages:
                []

        };

    }


    chatData[currentChat].messages.push({

        type:
            "sent",

        text:
            text,

        time:
            getCurrentTime()

    });


    input.value = "";


    renderMessages(
        currentChat
    );


    setTimeout(
        function () {

            addDemoReply();

        },
        1200
    );

}


// =====================================================
// DEMO REPLY
// =====================================================

function addDemoReply() {

    if (!chatData[currentChat]) {
        return;
    }


    chatData[currentChat].messages.push({

        type:
            "received",

        text:
            "Thank you for the message. I will check it.",

        time:
            getCurrentTime()

    });


    renderMessages(
        currentChat
    );

}


// =====================================================
// ENTER KEY TO SEND
// =====================================================

function handleMessageKey(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();

    }

}


// =====================================================
// SEARCH CONVERSATIONS
// =====================================================

function searchChats() {

    const input =
        document.getElementById(
            "chatSearch"
        );


    if (!input) {
        return;
    }


    const search =
        input.value
            .toLowerCase()
            .trim();


    document.querySelectorAll(
        ".conversation"
    ).forEach(function (chat) {

        const text =
            chat.innerText
                .toLowerCase();


        chat.style.display =
            text.includes(search)
                ? "flex"
                : "none";

    });

}


// =====================================================
// MOBILE CHAT SIDEBAR
// =====================================================

function openChatSidebar() {

    const sidebar =
        document.getElementById(
            "chatSidebar"
        );


    if (sidebar) {

        sidebar.classList.add(
            "active"
        );

    }

}


function closeChatSidebar() {

    const sidebar =
        document.getElementById(
            "chatSidebar"
        );


    if (sidebar) {

        sidebar.classList.remove(
            "active"
        );

    }

}


// =====================================================
// VOICE RECORDING
// =====================================================

let mediaRecorder =
    null;

let audioChunks =
    [];

let recordingInterval =
    null;

let recordingSeconds =
    0;


// =====================================================
// START RECORDING
// =====================================================

async function startRecording() {

    const panel =
        document.getElementById(
            "recordingPanel"
        );


    try {

        const stream =
            await navigator
                .mediaDevices
                .getUserMedia({
                    audio: true
                });


        mediaRecorder =
            new MediaRecorder(stream);


        audioChunks =
            [];


        mediaRecorder.ondataavailable =
            function (event) {

                if (
                    event.data.size > 0
                ) {

                    audioChunks.push(
                        event.data
                    );

                }

            };


        mediaRecorder.onstop =
            function () {

                const audioBlob =
                    new Blob(
                        audioChunks,
                        {
                            type:
                                "audio/webm"
                        }
                    );


                addVoiceMessage(
                    audioBlob
                );


                stream
                    .getTracks()
                    .forEach(
                        function (track) {

                            track.stop();

                        }
                    );

            };


        mediaRecorder.start();


        recordingSeconds =
            0;


        if (panel) {

            panel.classList.add(
                "active"
            );

        }


        recordingInterval =
            setInterval(
                updateRecordingTimer,
                1000
            );

    }


    catch (error) {

        alert(
            "Microphone permission is required to record a voice message."
        );

    }

}


// =====================================================
// STOP RECORDING
// =====================================================

function stopRecording() {

    if (
        mediaRecorder &&
        mediaRecorder.state !==
            "inactive"
    ) {

        mediaRecorder.stop();

    }


    clearInterval(
        recordingInterval
    );


    const panel =
        document.getElementById(
            "recordingPanel"
        );


    if (panel) {

        panel.classList.remove(
            "active"
        );

    }

}


// =====================================================
// RECORDING TIMER
// =====================================================

function updateRecordingTimer() {

    recordingSeconds++;


    const minutes =
        Math.floor(
            recordingSeconds / 60
        );


    const seconds =
        recordingSeconds % 60;


    const timer =
        document.getElementById(
            "recordingTimer"
        );


    if (timer) {

        timer.textContent =
            String(minutes).padStart(
                2,
                "0"
            )
            +
            ":"
            +
            String(seconds).padStart(
                2,
                "0"
            );

    }

}


// =====================================================
// ADD VOICE MESSAGE
// =====================================================

function addVoiceMessage(
    audioBlob
) {

    if (!chatData[currentChat]) {
        return;
    }


    const audioURL =
        URL.createObjectURL(
            audioBlob
        );


    chatData[currentChat]
        .messages
        .push({

            type:
                "sent",

            voice:
                true,

            audioURL:
                audioURL,

            duration:
                formatDuration(
                    recordingSeconds
                ),

            time:
                getCurrentTime()

        });


    renderMessagesWithAudio(
        currentChat
    );

}


// =====================================================
// RENDER CHAT WITH AUDIO
// =====================================================

function renderMessagesWithAudio(
    name
) {

    const messagesArea =
        document.getElementById(
            "messagesArea"
        );


    if (!messagesArea) {
        return;
    }


    messagesArea.innerHTML = `

        <div class="chat-date">
            Today
        </div>

    `;


    chatData[name]
        .messages
        .forEach(function (message) {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "message-row " +
                message.type;


            if (message.voice) {

                const audio =
                    document.createElement(
                        "audio"
                    );


                audio.src =
                    message.audioURL || "";


                audio.style.display =
                    "none";


                const voice =
                    document.createElement(
                        "div"
                    );


                voice.className =
                    "voice-message";


                const button =
                    document.createElement(
                        "button"
                    );


                button.className =
                    "play-voice";


                button.textContent =
                    "▶";


                button.onclick =
                    function () {

                        if (
                            audio.paused
                        ) {

                            audio.play();

                            button.textContent =
                                "⏸";

                        }

                        else {

                            audio.pause();

                            button.textContent =
                                "▶";

                        }

                    };


                const wave =
                    document.createElement(
                        "div"
                    );


                wave.className =
                    "voice-wave";


                for (
                    let i = 0;
                    i < 8;
                    i++
                ) {

                    const bar =
                        document.createElement(
                            "span"
                        );


                    wave.appendChild(
                        bar
                    );

                }


                const duration =
                    document.createElement(
                        "span"
                    );


                duration.className =
                    "voice-duration";


                duration.textContent =
                    message.duration;


                voice.appendChild(
                    button
                );


                voice.appendChild(
                    wave
                );


                voice.appendChild(
                    duration
                );


                row.appendChild(
                    voice
                );


                row.appendChild(
                    audio
                );

            }


            else {

                const bubble =
                    document.createElement(
                        "div"
                    );


                bubble.className =
                    "message-bubble";


                bubble.innerHTML = `

                    <p>
                        ${escapeHTML(
                            message.text
                        )}
                    </p>

                    <span class="message-time">

                        ${message.time}

                    </span>

                `;


                row.appendChild(
                    bubble
                );

            }


            messagesArea.appendChild(
                row
            );

        });


    messagesArea.scrollTop =
        messagesArea.scrollHeight;

}


// =====================================================
// DEMO VOICE PLAY BUTTON
// =====================================================

function playVoiceMessage(button) {

    button.classList.toggle(
        "playing"
    );


    button.textContent =
        button.classList.contains(
            "playing"
        )
            ? "⏸"
            : "▶";

}


// =====================================================
// CURRENT TIME
// =====================================================

function getCurrentTime() {

    const now =
        new Date();


    return now.toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


// =====================================================
// FORMAT RECORDING TIME
// =====================================================

function formatDuration(
    seconds
) {

    const minutes =
        Math.floor(
            seconds / 60
        );


    const remaining =
        seconds % 60;


    return (
        minutes +
        ":" +
        String(
            remaining
        ).padStart(
            2,
            "0"
        )
    );

}


// =====================================================
// SECURITY
// =====================================================

function escapeHTML(text) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        text;


    return div.innerHTML;

}


// =====================================================
// INITIALIZE CHAT
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        if (
            document.getElementById(
                "messagesArea"
            )
        ) {

            renderMessages(
                currentChat
            );

        }

    }
);


// =====================================================
// GOVERNMENT SCHEME ELIGIBILITY CHECKER
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const schemeForm =
            document.getElementById(
                "schemeEligibilityForm"
            );


        const resultsContainer =
            document.getElementById(
                "schemeResults"
            );


        const resetButton =
            document.getElementById(
                "schemeResetBtn"
            );


        if (!schemeForm) {
            return;
        }


        schemeForm.addEventListener(
            "submit",
            function (event) {

                event.preventDefault();


                const studentClass =
                    document.getElementById(
                        "studentClass"
                    )?.value;


                const category =
                    document.getElementById(
                        "studentCategory"
                    )?.value;


                const income =
                    Number(
                        document.getElementById(
                            "familyIncome"
                        )?.value || 0
                    );


                const disability =
                    document.getElementById(
                        "disability"
                    )?.checked;


                const girlStudent =
                    document.getElementById(
                        "girlStudent"
                    )?.checked;


                const eligibleSchemes =
                    [];


                if (studentClass) {

                    eligibleSchemes.push({

                        icon:
                            "🎓",

                        name:
                            "School Education Support Scheme",

                        description:
                            "Education assistance available for eligible government school students.",

                        status:
                            "Eligible"

                    });

                }


                if (
                    income > 0 &&
                    income <= 250000
                ) {

                    eligibleSchemes.push({

                        icon:
                            "💰",

                        name:
                            "Student Financial Assistance Scheme",

                        description:
                            "Financial support for students from eligible low-income families.",

                        status:
                            "Eligible"

                    });

                }


                if (girlStudent) {

                    eligibleSchemes.push({

                        icon:
                            "👧",

                        name:
                            "Girl Child Education Support",

                        description:
                            "Additional educational support available for eligible girl students.",

                        status:
                            "Eligible"

                    });

                }


                if (disability) {

                    eligibleSchemes.push({

                        icon:
                            "♿",

                        name:
                            "Student Disability Support Scheme",

                        description:
                            "Additional educational assistance for students with disabilities.",

                        status:
                            "Eligible"

                    });

                }


                displaySchemeResults(
                    eligibleSchemes
                );

            }
        );


        function displaySchemeResults(
            schemes
        ) {

            if (!resultsContainer) {
                return;
            }


            resultsContainer.innerHTML =
                "";


            const title =
                document.createElement(
                    "div"
                );


            title.className =
                "scheme-results-title";


            title.textContent =
                schemes.length > 0

                    ? `Schemes You May Be Eligible For (${schemes.length})`

                    : "No Matching Schemes Found";


            resultsContainer.appendChild(
                title
            );


            if (schemes.length === 0) {

                const noResult =
                    document.createElement(
                        "div"
                    );


                noResult.className =
                    "scheme-no-result";


                noResult.innerHTML = `

                    <div class="scheme-no-result-icon">
                        🔍
                    </div>

                    <h3>
                        No matching schemes found
                    </h3>

                    <p>
                        Based on the information entered,
                        we could not find a matching scheme.
                        You can try checking the details again.
                    </p>

                `;


                resultsContainer.appendChild(
                    noResult
                );

            }


            else {

                schemes.forEach(
                    function (scheme) {

                        const card =
                            document.createElement(
                                "div"
                            );


                        card.className =
                            "scheme-result-card";


                        card.innerHTML = `

                            <div class="scheme-result-icon">
                                ${scheme.icon}
                            </div>

                            <div class="scheme-result-content">

                                <h3>
                                    ${scheme.name}
                                </h3>

                                <p>
                                    ${scheme.description}
                                </p>

                            </div>

                            <div class="scheme-status">
                                ${scheme.status}
                            </div>

                        `;


                        resultsContainer.appendChild(
                            card
                        );

                    }
                );

            }


            resultsContainer.classList.add(
                "show"
            );


            setTimeout(
                function () {

                    resultsContainer.scrollIntoView(
                        {
                            behavior:
                                "smooth",

                            block:
                                "start"
                        }
                    );

                },
                100
            );

        }


        if (resetButton) {

            resetButton.addEventListener(
                "click",
                function () {

                    schemeForm.reset();


                    if (resultsContainer) {

                        resultsContainer.classList.remove(
                            "show"
                        );

                        resultsContainer.innerHTML =
                            "";

                    }


                    window.scrollTo({

                        top:
                            0,

                        behavior:
                            "smooth"

                    });

                }
            );

        }

    }
);


// =====================================================
// ATTENDANCE MANAGEMENT
// =====================================================

let attendanceRecords = {

    "Rahul Kumar":
        "Present",

    "Anita Das":
        "Present",

    "Riya Singh":
        "Present",

    "Arjun Behera":
        "Present",

    "Sneha Patel":
        "Present"

};


function setAttendance(
    button,
    status
) {

    const row =
        button.closest(
            ".student-attendance-row"
        );


    if (!row) {
        return;
    }


    const nameElement =
        row.querySelector(
            ".student-information h3"
        );


    if (!nameElement) {
        return;
    }


    const studentName =
        nameElement.textContent.trim();


    const buttons =
        row.querySelectorAll(
            ".attendance-status-btn"
        );


    buttons.forEach(
        function (btn) {

            btn.classList.remove(
                "selected"
            );

        }
    );


    button.classList.add(
        "selected"
    );


    attendanceRecords[
        studentName
    ] = status;


    updateAttendanceSummary();

}


function updateAttendanceSummary() {

    const students =
        Object.keys(
            attendanceRecords
        );


    const total =
        students.length;


    let present = 0;

    let absent = 0;


    students.forEach(
        function (student) {

            if (
                attendanceRecords[
                    student
                ] === "Present"
            ) {

                present++;

            }


            if (
                attendanceRecords[
                    student
                ] === "Absent"
            ) {

                absent++;

            }

        }
    );


    const percentage =
        total === 0
            ? 0
            : Math.round(
                (present / total) * 100
            );


    const totalElement =
        document.getElementById(
            "totalStudents"
        );


    const presentElement =
        document.getElementById(
            "presentCount"
        );


    const absentElement =
        document.getElementById(
            "absentCount"
        );


    const percentageElement =
        document.getElementById(
            "attendancePercentage"
        );


    if (totalElement) {

        totalElement.textContent =
            total;

    }


    if (presentElement) {

        presentElement.textContent =
            present;

    }


    if (absentElement) {

        absentElement.textContent =
            absent;

    }


    if (percentageElement) {

        percentageElement.textContent =
            percentage + "%";

    }

}


function saveAttendance() {

    updateAttendanceSummary();


    const present =
        Object.values(
            attendanceRecords
        ).filter(
            status =>
                status === "Present"
        ).length;


    const absent =
        Object.values(
            attendanceRecords
        ).filter(
            status =>
                status === "Absent"
        ).length;


    alert(

        "Attendance saved successfully!\n\n" +

        "Present: " +
        present +

        "\n" +

        "Absent: " +
        absent

    );

}


document.addEventListener(
    "DOMContentLoaded",
    function () {

        const dateElement =
            document.getElementById(
                "attendanceDate"
            );


        if (dateElement) {

            const today =
                new Date();


            dateElement.textContent =
                today.toLocaleDateString(
                    "en-IN",
                    {
                        day:
                            "2-digit",

                        month:
                            "short",

                        year:
                            "numeric"
                    }
                );

        }


        updateAttendanceSummary();

    }
);


// =====================================================
// STUDENT MARKS MANAGEMENT
// =====================================================

function calculateMarks(input) {

    const row =
        input.closest(
            ".student-marks-row"
        );


    if (!row) {
        return;
    }


    const inputs =
        row.querySelectorAll(
            ".mark-input"
        );


    let total = 0;


    inputs.forEach(
        function (field) {

            let value =
                Number(
                    field.value
                );


            if (isNaN(value)) {

                value = 0;

            }


            if (value < 0) {

                value = 0;

                field.value =
                    0;

            }


            if (value > 100) {

                value = 100;

                field.value =
                    100;

            }


            total += value;

        }
    );


    const average =
        inputs.length > 0

            ? total / inputs.length

            : 0;


    const totalElement =
        row.querySelector(
            ".student-total"
        );


    const averageElement =
        row.querySelector(
            ".student-average"
        );


    if (totalElement) {

        totalElement.textContent =
            total;

    }


    if (averageElement) {

        averageElement.textContent =
            average.toFixed(1) + "%";

    }

}


function saveMarks() {

    const rows =
        document.querySelectorAll(
            ".student-marks-row"
        );


    if (rows.length === 0) {
        return;
    }


    let message =
        "Marks saved successfully!\n\n";


    rows.forEach(
        function (row) {

            const nameElement =
                row.querySelector(
                    ".marks-student h3"
                );


            const totalElement =
                row.querySelector(
                    ".student-total"
                );


            const averageElement =
                row.querySelector(
                    ".student-average"
                );


            if (
                !nameElement ||
                !totalElement ||
                !averageElement
            ) {

                return;

            }


            message +=

                nameElement.textContent.trim() +

                " — Total: " +

                totalElement.textContent.trim() +

                " | Average: " +

                averageElement.textContent.trim() +

                "\n";

        }
    );


    alert(message);

}


document.addEventListener(
    "DOMContentLoaded",
    function () {

        const rows =
            document.querySelectorAll(
                ".student-marks-row"
            );


        rows.forEach(
            function (row) {

                const input =
                    row.querySelector(
                        ".mark-input"
                    );


                if (input) {

                    calculateMarks(
                        input
                    );

                }

            }
        );

    }
);


// =====================================================
// ADMIN DASHBOARD
// =====================================================


// Current date

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const dateElement =
            document.getElementById(
                "adminCurrentDate"
            );


        if (dateElement) {

            const today =
                new Date();


            dateElement.textContent =
                today.toLocaleDateString(
                    "en-IN",
                    {
                        day:
                            "2-digit",

                        month:
                            "short",

                        year:
                            "numeric"
                    }
                );

        }

    }
);


// Admin search

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const searchInput =
            document.getElementById(
                "adminSearch"
            );


        if (!searchInput) {
            return;
        }


        searchInput.addEventListener(
            "input",
            function () {

                const searchValue =
                    this.value
                        .toLowerCase()
                        .trim();


                const studentRows =
                    document.querySelectorAll(
                        "#studentTableBody tr"
                    );


                const teacherRows =
                    document.querySelectorAll(
                        "#teacherTableBody tr"
                    );


                studentRows.forEach(
                    function (row) {

                        const text =
                            row.textContent
                                .toLowerCase();


                        row.style.display =
                            text.includes(
                                searchValue
                            )
                                ? ""
                                : "none";

                    }
                );


                teacherRows.forEach(
                    function (row) {

                        const text =
                            row.textContent
                                .toLowerCase();


                        row.style.display =
                            text.includes(
                                searchValue
                            )
                                ? ""
                                : "none";

                    }
                );

            }
        );

    }
);


// Admin stat action

function adminStatAction(type) {

    switch (type) {

        case "students":

            document
                .querySelector(
                    ".admin-table-panel"
                )
                ?.scrollIntoView({
                    behavior:
                        "smooth"
                });

            break;


        case "teachers":

            document
                .querySelectorAll(
                    ".admin-table-panel"
                )[1]
                ?.scrollIntoView({
                    behavior:
                        "smooth"
                });

            break;


        case "attendance":

            document
                .querySelector(
                    ".attendance-analytics-panel"
                )
                ?.scrollIntoView({
                    behavior:
                        "smooth"
                });

            break;


        case "risk":

            alert(
                "Students requiring follow-up are identified based on attendance or academic performance."
            );

            break;

    }

}


// View student

function viewStudent(studentName) {

    alert(

        "Student Details\n\n" +

        "Name: " +
        studentName

    );

}


// View teacher

function viewTeacher(teacherName) {

    alert(

        "Teacher Details\n\n" +

        "Name: " +
        teacherName

    );

}


// View all students

function showAllStudents() {

    alert(
        "Student Management\n\n" +
        "This button is ready to connect to the complete student management page."
    );

}


// View all teachers

function showAllTeachers() {

    alert(
        "Teacher Management\n\n" +
        "This button is ready to connect to the complete teacher management page."
    );

}


// Admin reports

function downloadAdminReport(
    reportType
) {

    let reportName =
        "";


    switch (reportType) {

        case "attendance":

            reportName =
                "Attendance Report";

            break;


        case "performance":

            reportName =
                "Student Performance Report";

            break;


        case "teacher":

            reportName =
                "Teacher Report";

            break;

    }


    alert(

        reportName +

        "\n\nReport generation selected.\n" +

        "This can be connected to Flask/Python to generate a real PDF or CSV report."

    );

}


// =====================================================
// LOGIN + SIGNUP SWITCHER
// =====================================================

function switchAuthMode(
    mode
) {

    const loginForm =
        document.getElementById(
            "loginForm"
        );


    const signupForm =
        document.getElementById(
            "signupForm"
        );


    const loginTab =
        document.getElementById(
            "loginTab"
        );


    const signupTab =
        document.getElementById(
            "signupTab"
        );


    const authTitle =
        document.getElementById(
            "authTitle"
        );


    const authSubtitle =
        document.getElementById(
            "authSubtitle"
        );


    const bottomText =
        document.getElementById(
            "authBottomText"
        );


    const bottomButton =
        document.getElementById(
            "authBottomButton"
        );


    if (
        !loginForm ||
        !signupForm ||
        !loginTab ||
        !signupTab
    ) {

        return;

    }


    if (mode === "signup") {

        loginForm.classList.add(
            "hidden"
        );

        signupForm.classList.remove(
            "hidden"
        );

        loginTab.classList.remove(
            "active"
        );

        signupTab.classList.add(
            "active"
        );


        if (authTitle) {

            authTitle.textContent =
                "Create Your Account ✨";

        }


        if (authSubtitle) {

            authSubtitle.textContent =
                "Join Parent-Teacher Bridge and stay connected";

        }


        if (bottomText) {

            bottomText.textContent =
                "Already have an account?";

        }


        if (bottomButton) {

            bottomButton.textContent =
                "Login";


            bottomButton.onclick =
                function () {

                    switchAuthMode(
                        "login"
                    );

                };

        }

    }


    else {

        signupForm.classList.add(
            "hidden"
        );

        loginForm.classList.remove(
            "hidden"
        );

        signupTab.classList.remove(
            "active"
        );

        loginTab.classList.add(
            "active"
        );


        if (authTitle) {

            authTitle.textContent =
                "Welcome Back 👋";

        }


        if (authSubtitle) {

            authSubtitle.textContent =
                "Login to your Parent-Teacher Bridge account";

        }


        if (bottomText) {

            bottomText.textContent =
                "Don't have an account?";

        }


        if (bottomButton) {

            bottomButton.textContent =
                "Sign Up";


            bottomButton.onclick =
                function () {

                    switchAuthMode(
                        "signup"
                    );

                };

        }

    }

}


// =====================================================
// PASSWORD VISIBILITY
// =====================================================

function togglePassword(
    inputId,
    button
) {

    const input =
        document.getElementById(
            inputId
        );


    if (!input) {
        return;
    }


    if (
        input.type ===
        "password"
    ) {

        input.type =
            "text";


        if (button) {

            button.textContent =
                "🙈";

        }

    }


    else {

        input.type =
            "password";


        if (button) {

            button.textContent =
                "👁";

        }

    }

}


// =====================================================
// SIGNUP PASSWORD VALIDATION
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const signupForm =
            document.getElementById(
                "signupForm"
            );


        if (!signupForm) {
            return;
        }


        signupForm.addEventListener(
            "submit",
            function (event) {

                const passwordElement =
                    document.getElementById(
                        "signupPassword"
                    );


                const confirmElement =
                    document.getElementById(
                        "signupConfirmPassword"
                    );


                if (
                    !passwordElement ||
                    !confirmElement
                ) {

                    return;

                }


                const password =
                    passwordElement.value;


                const confirmPassword =
                    confirmElement.value;


                if (
                    password !==
                    confirmPassword
                ) {

                    event.preventDefault();


                    alert(
                        "Passwords do not match. Please try again."
                    );


                    return;

                }


                if (
                    password.length < 6
                ) {

                    event.preventDefault();


                    alert(
                        "Password must contain at least 6 characters."
                    );

                }

            }
        );

    }
);