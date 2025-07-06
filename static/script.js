let mediaRecorder;
let audioChunks = [];

const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const answerBox = document.getElementById('answerBox');

recordBtn.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = event => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64Audio = reader.result;

      answerBox.innerHTML = "⏳ Transcribing & thinking...";
      const res = await fetch("/transcribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ audio: base64Audio })
      });

      const data = await res.json();
      answerBox.innerHTML = `<b>Q:</b> ${data.question}<br><br><b>A:</b> ${data.answer}`;
    };

    reader.readAsDataURL(audioBlob);
  };

  audioChunks = [];
  mediaRecorder.start();
  recordBtn.disabled = true;
  stopBtn.disabled = false;
};

stopBtn.onclick = () => {
  mediaRecorder.stop();
  recordBtn.disabled = false;
  stopBtn.disabled = true;
};
