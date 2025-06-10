const questions = [
    "پایتخت ایران چیست؟",
    "۵ + ۳ چند می‌شود؟",
    "HTML مخفف چیست؟",
    "چه سالی میلادی هستیم؟",
    "چه زبانی برای یادگیری ماشین مناسب است؟"
];

let currentIndex = 0;
let answers = [];
let times = [];

let savedData = localStorage.getItem('currentIndex');
if (savedData !== null){
    currentIndex = JSON.parse(savedData);
}
savedData = localStorage.getItem('answers');
if (savedData !== null) {
    answers = JSON.parse(savedData);
}
savedData = localStorage.getItem('times');
if (savedData !== null) {
    times = JSON.parse(savedData);
}


const questionDiv = document.getElementById("question");
const answerField = document.getElementById("answer");
const progressDiv = document.getElementById("progress");
const modeBtn = document.getElementById("modeBtn");

function showProgress() {
    progressDiv.innerHTML = "";
    for (let i = 0; i < questions.length; i++) {
        const circle = document.createElement("div");
        circle.classList.add("circle");
        if (i < currentIndex) circle.classList.add("done");
        else if (i === currentIndex) circle.classList.add("current");
        progressDiv.appendChild(circle);
    }
}

function showQuestion() {
    questionDiv.textContent = questions[currentIndex];
    answerField.value = answers[currentIndex] || "";
    if (currentIndex === questions.length-1) {
        document.getElementById("next-btn").innerText = "ثبت";
    } else {
        document.getElementById("next-btn").innerText = "بعدی";
    }
    showProgress();
}

function saveAnswer() {
    answers[currentIndex] = answerField.value;
    const now = new Date();
    times[currentIndex] = now.getSeconds();
    localStorage.setItem('currentIndex', JSON.stringify(currentIndex));
    localStorage.setItem('answers', JSON.stringify(answers));
    localStorage.setItem('times', JSON.stringify(times));
}

function nextQuestion() {
    saveAnswer();
    if (currentIndex < questions.length - 1) {
        currentIndex++;
        showQuestion();
    }else{

        const confirmed = confirm("آیا مطمئنی می‌خواهی ثبت کنی؟");

        if (confirmed) {
            const formatted = answers.map((desc, index) => ({
                qnumber: index + 1,
                description: desc,
                time_taken: times[index]
            }));

            fetch('/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formatted)
            }).then(() => {
                window.location.href = "/end_quiz/";  // اینجا میره به صفحه بعدی
            });
        }
    }
}

function prevQuestion() {
    saveAnswer();
    if (currentIndex > 0) {
        currentIndex--;
        showQuestion();
    }
}

function updateThemeLabel() {
    if (document.body.classList.contains("dark")) {
    modeBtn.textContent = "dark";
    } else {
    modeBtn.textContent = "light";
    }
}

function toggleTheme() {
    document.body.classList.toggle("dark");
    localStorage.setItem("theme", document.body.classList.contains("dark") ? "dark" : "light");
    updateThemeLabel();
}

(function () {
    if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark");
    }
    updateThemeLabel();
    showQuestion();
})();