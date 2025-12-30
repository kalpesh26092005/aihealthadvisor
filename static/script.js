// login query
document.querySelector('form').addEventListener('submit', function (e) {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value.trim();

  if (!email || !password) {
    e.preventDefault();
    alert("Please enter email and password.");
  }
});



  const diseaseDB = [
    { name: "Common Cold", desc: "Mild viral infection of nose and throat.", severity: "mild" },
    { name: "Flu", desc: "Influenza virus that causes fever, chills and fatigue.", severity: "moderate" },
    { name: "COVID-19", desc: "Respiratory illness with fever, cough, and loss of taste.", severity: "moderate" },
    { name: "Migraine", desc: "Severe headache, nausea, and sensitivity to light.", severity: "moderate" },
    { name: "Pneumonia", desc: "Lung infection that causes cough, fever, and difficulty breathing.", severity: "severe" },
    { name: "Sinusitis", desc: "Inflammation of sinuses causing pressure and facial pain.", severity: "mild" },
    { name: "Cough", desc: "A reflex action to clear your airways, common in respiratory infections.",severity: "mild"},
    { name: "Headache", desc: "Pain or pressure in the head, often caused by stress, dehydration, or illness.", severity: "mild"},
    { name: "Sore Throat", desc: "Pain, scratchiness or irritation in the throat, often worsened when swallowing.", severity: "mild"},
    { name: "Sore Throat", desc: "Pain, scratchiness or irritation in the throat, often worsened when swallowing.", severity: "mild"},
  { name: "Fatigue", desc: "A persistent feeling of tiredness or exhaustion not relieved by rest.", severity: "moderate"},
  { name: "Shortness of Breath", desc: "Difficulty in breathing or feeling out of breath.", severity: "severe"},
  { name: "Runny Nose", desc: "Excess mucus drainage from the nose, often a sign of cold or allergies.", severity: "mild"},
  { name: "Sneezing", desc: "A sudden burst of air through the nose and mouth, often due to allergies or colds.", severity: "mild"},
  { name: "Nausea", desc: "A feeling of sickness with an inclination to vomit." , severity: "moderate"},
  { name: "Vomiting", desc: "Forceful discharge of stomach contents through the mouth.",severity: "moderate"},
  { name: "Diarrhea", desc: "Loose, watery stools that occur more frequently than usual.",severity: "moderate"},
  { name: "Chest Pain", desc: "Discomfort or pain in the chest area; can indicate heart or lung issues.",severity: "seve"},
  { name: "Chills", desc: "Feeling cold with shivering, often occurring with fever." , severity: "mild"},
  { name: "Dizziness", desc: "A sensation of spinning or losing one's balance.",severity: "modera"},
  { name: "Loss of Taste or Smell", desc: "Partial or complete loss of these senses, often linked with viral infections.",severity: "moderate"},
  { name: "Skin Rash", desc: "An area of irritated or swollen skin, often itchy or painful.", severity: "mild"},
  { name: "Muscle Pain", desc: "Discomfort or pain in muscles, often caused by infection, overuse or injury.", severity: "mild"},
  { name: "Joint Pain", desc: "Pain, stiffness, or swelling in joints, common in arthritis or viral infections.",severity: "moderate"},
  { name: "Abdominal Pain", desc: "Pain occurring anywhere in the belly; could signal digestive issues.",severity: "moderate"},
  { name: "Difficulty Sleeping", desc: "Inability to fall or stay asleep, possibly due to anxiety or health conditions.", severity: "mild" }
    
];

  document.querySelector('.symptoms-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const input = document.querySelector('.symptoms-form input').value.trim();
    if (!input) return;

    const symptoms = input.toLowerCase().split(',').map(s => s.trim());
    const matched = diseaseDB.filter(d =>
      symptoms.some(sym => d.desc.toLowerCase().includes(sym) || d.name.toLowerCase().includes(sym))
    );

    const resultSection = document.getElementById("disease-result");
    const resultCards = document.getElementById("result-cards");
    resultCards.innerHTML = "";

    if (matched.length === 0) {
      resultCards.innerHTML = `<p>No matching conditions found. Try different symptoms.</p>`;
    } else {
      matched.forEach(d => {
        resultCards.innerHTML += `
          <div class="result-card">
            <h3>${d.name}</h3>
            <p>${d.desc}</p>
            <span class="tag ${d.severity}">${d.severity.charAt(0).toUpperCase() + d.severity.slice(1)}</span>
          </div>
        `;
      });
    }

    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: "smooth" });
  });

  // When displaying the analysis result
function displayAnalysis(result) {
    let displayText = result;
    
    if (typeof result === 'object') {
        displayText = JSON.stringify(result, null, 2);
    }
    
    // Replace \n with line breaks for HTML display
    displayText = displayText.replace(/\\n/g, '\n');
    
    // For HTML element
    document.getElementById('result').innerHTML = displayText.replace(/\n/g, '<br>');
    
    // For console/logging
    console.log(displayText);
}

  

