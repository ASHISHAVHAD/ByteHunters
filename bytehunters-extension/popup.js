const API_URL = "http://127.0.0.1:5000/api/verify";

document.getElementById('verifyBtn').addEventListener('click', () => {
  const text = document.getElementById('textInput').value;
  if(!text) { alert("Please enter some text first."); return; }
  runVerification(text, 'text');
});

document.getElementById('verifyUrlBtn').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    runVerification(tabs[0].url, 'url');
  });
});

async function runVerification(content, type) {
  const loader = document.getElementById('loader');
  const container = document.getElementById('claims-container');

  loader.style.display = 'block';
  container.style.display = 'none';
  container.innerHTML = '';

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: content, input_type: type })
    });

    const json = await response.json();
    loader.style.display = 'none';

    if (json.status === 'success') {
      const claims = json.data.claims;
      container.style.display = 'block';
      
      if(claims.length > 0) {
        claims.forEach(claim => {
            const cardHtml = `
                <div class="claim-card status-${claim.claim_validity}">
                    <div class="claim-header">
                        <span class="badge bg-${claim.claim_validity}">${claim.claim_validity}</span>
                        <span class="conf-score">${claim.confidence}% Conf.</span>
                    </div>
                    <div class="claim-text">"${claim.claim_text}"</div>
                    <div class="claim-reason">${claim.reasoning}</div>
                </div>
            `;
            container.innerHTML += cardHtml;
        });

      } else {
        container.innerHTML = "<p style='text-align:center; color:#666;'>No specific verifiable claims found in this content.</p>";
      }
    } else {
      alert("Server Error: " + json.message);
    }
  } catch (err) {
    loader.style.display = 'none';
    alert("Could not connect to ByteHunters server. Make sure 'app.py' is running!");
    console.error(err);
  }
}