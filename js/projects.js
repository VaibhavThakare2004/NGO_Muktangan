const projectData = [
  {
    name: "Anandi Aai Anandi Bal",
    desc: `Project is focused on improving maternal and child health outcomes. The project's goals include:
1. Promoting early pregnancy registration
2. Ensuring regular ANC (Antenatal Care) checkups
3. Raising awareness about the importance of these checkups

The project also targets specific health issues such as SAM and MAM children. Additionally, we are working with community health workers (ASHA workers) to identify and register pregnancies early. It empowers women with knowledge to ensure a healthy pregnancy and a healthy child.

Impact Vision:
A future where every child is born free from preventable genetic blood disorders and every mother enjoys a healthy, stress-free motherhood.`,
    stats: [
      { label: "Mothers Helped", value: "2,500+" },
      { label: "Districts", value: "15" },
      { label: "Avg Monthly Reach", value: "500+" },
      { label: "Completion", value: "85%" }
    ],
    gallery: ["img/anandi1.jpg", "img/anandi2.jpg", "img/anandi3.jpg"]
  },
  {
    name: "Thalassemia Mukt Bharat",
    desc: `Preventing Genetic Disorders, Protecting Future Generations

The Thalassemia-Free India Project is a nationwide preventive health campaign aimed at eliminating Thalassemia and Sickle Cell Disease through early diagnosis, awareness, and proactive testing.
Focus: HPLC Testing in Panchayats, Schools, and Colleges

                                  Objectives:
1. To conduct mass HPLC screening of students and youth across 
all gram panchayats, schools, and colleges.
2. To identify carriers of Thalassemia and Sickle Cell Disease before 
marriage or pregnancy.
3. To integrate screening with genetic counseling & preventive 
awareness programs.

Vision:
A Thalassemia-Free Generation where every youth is aware of their genetic status, and every village takes collective responsibility for preventing inherited blood disorders.

Slogan:
“Test Today, Protect Tomorrow – Say Yes to HPLC Screening!”`,
    stats: [
      { label: "Mothers Helped", value: "2,500+" },
      { label: "Districts", value: "15" },
      { label: "Avg Monthly Reach", value: "500+" },
      { label: "Completion", value: "85%" }
    ],
    gallery: ["img/thal1.jpg", "img/thal2.jpg", "img/thal3.jpg"]
  },
  {
    name: "Cancer awareness",
    desc: `A cancer awareness project in the panchayat involves:
    
1. Awareness campaigns: Organizing events, workshops, and campaigns 
to educate people about cancer risks, symptoms, and early detection methods.
2. Screenings and health camps: Providing free or low-cost screenings for 
common cancers, such as breast, cervical, and oral cancer.
3. Education and counseling: Offering guidance on healthy lifestyles, tobacco cessation,and nutrition to reduce cancer risk.
4. Support groups: Creating support networks for cancer patients and their families.
5. Collaboration with healthcare providers: Partnering with local healthcare
providers to improve access to cancer diagnosis, treatment, and care.

The goal is to empower the community with knowledge and resources to prevent, detect, and manage cancer effectively.`,
    stats: [
      { label: "Mothers Helped", value: "2,500+" },
      { label: "Districts", value: "15" },
      { label: "Avg Monthly Reach", value: "500+" },
      { label: "Completion", value: "85%" }
    ],
    gallery: ["img/cancer1.jpg", "img/cancer2.jpg", "img/cancer3.jpg"]
  }
];

// Show modal when clicking project cards
document.querySelectorAll('.project-card').forEach((card) => {
  card.addEventListener('click', function () {
    const index = parseInt(card.getAttribute('data-project'));
    showModal(index);
  });
});

function showModal(idx) {
  const modal = document.getElementById('projectModal');
  const details = document.getElementById('modalDetails');
  const gallery = document.getElementById('modalGallery');
  const project = projectData[idx];

  const fullText = project.desc.replace(/\n/g, "<br>");
  const shortText = project.desc.split('\n')[0];

  // Fill modal content
  details.innerHTML = `
    <h2>${project.name}</h2>
    <div class="modal-desc">
      <span class="short-text">${shortText}...</span>
      <span class="full-text" style="display: none;">${fullText}</span>
      <div class="toggle-read" style="color: #a100a1; cursor: pointer; margin-top: 10px; font-weight: bold;">Read more ▼</div>
    </div>
    <div class="modal-stats">
      ${project.stats.map(stat => `
        <div class="stat">
          <span>${stat.value}</span><br>
          <span>${stat.label}</span>
        </div>`).join('')}
    </div>
  `;

  // Fill gallery
  gallery.innerHTML = project.gallery.map(img => `
    <img src="${img}" alt="${project.name} photo">
  `).join('');

  modal.classList.add('active');

  // Toggle logic
  const toggle = document.querySelector('.toggle-read');
  const shortSpan = document.querySelector('.short-text');
  const fullSpan = document.querySelector('.full-text');

  toggle.addEventListener('click', function () {
    const isExpanded = fullSpan.style.display === 'inline';
    fullSpan.style.display = isExpanded ? 'none' : 'inline';
    shortSpan.style.display = isExpanded ? 'inline' : 'none';
    toggle.innerHTML = isExpanded ? 'Read more ▼' : 'Read less ▲';
  });
}

// Close modal
document.getElementById('closeModal').addEventListener('click', () => {
  document.getElementById('projectModal').classList.remove('active');
});

// Close modal when clicking outside
document.getElementById('projectModal').addEventListener('click', (e) => {
  if (e.target.id === 'projectModal') {
    document.getElementById('projectModal').classList.remove('active');
  }
});
