let mediaRecorder;
let audioChunks = [];

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const answerBox = document.getElementById("answer");

startBtn.onclick = async () => {
  answerBox.innerText = "Listening...";
  audioChunks = [];

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
    const reader = new FileReader();
    reader.readAsDataURL(audioBlob);
    reader.onloadend = async () => {
      const base64Audio = reader.result;

      const response = await fetch("/transcribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ audio: base64Audio }),
      });

      const data = await response.json();
      if (data.answer) {
        answerBox.innerText = `🗣️ Q: ${data.question}\n\n💬 A: ${data.answer}`;
      } else {
        answerBox.innerText = `❌ Error: ${data.error}`;
      }
    };
  };

  mediaRecorder.start();
  startBtn.disabled = true;
  stopBtn.disabled = false;
};

stopBtn.onclick = () => {
  mediaRecorder.stop();
  startBtn.disabled = false;
  stopBtn.disabled = true;
};
        
