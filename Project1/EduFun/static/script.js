document.addEventListener('DOMContentLoaded', function () {
  const map = L.map('map').setView([51.4416, 5.4697], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  let pinPlaced = false;
  const modal = document.getElementById('eventModal');
  const addPinBtn = document.getElementById('addPinBtn');

  map.on('click', function (e) {
    if (!pinPlaced) {
      L.marker(e.latlng).addTo(map);
      pinPlaced = true;
    }
  });

  addPinBtn.addEventListener('click', () => {
    if (pinPlaced && modal) {
      modal.classList.remove('hidden');
    }
  });

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.add('hidden');
      }
    });
  }
});


