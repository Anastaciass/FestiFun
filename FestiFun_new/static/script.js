let lastLat = null;
let lastLng = null;

document.addEventListener('DOMContentLoaded', function () {
  const map = L.map('map').setView([51.4416, 5.4697], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  fetch("/get_events")
  .then(res => res.json())
  .then(events => {
    events.forEach(evt => {
      const popupContent = `
        <div style="max-width: 200px;">
          <strong>${evt.topic || 'without topic'}</strong><br>
          <em>${evt.description || 'no description'}</em><br>
          <span> amount in $: ${evt.price || 'free'}</span><br>
          ${evt.webpage ? `<a href="${evt.webpage}" target="_blank">webpage</a><br>` : ''}
          ${evt.image ? `<img src="${evt.image}" alt="Image" style="width: 100%; margin-top: 5px; border-radius: 8px;">` : ''}
        </div>
      `;
      L.marker([parseFloat(evt.lat), parseFloat(evt.lng)])
        .addTo(map)
        .bindPopup(popupContent);
    });
  });

  let pinPlaced = false;
  const modal = document.getElementById('eventModal');
  const addPinBtn = document.getElementById('addPinBtn');

  map.on('click', function (e) {
    if (!pinPlaced) {
      L.marker(e.latlng).addTo(map);
      lastLat = e.latlng.lat;
      lastLng = e.latlng.lng;
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

  const form = document.getElementById("eventForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      if (!lastLat || !lastLng) {
        alert("Click on map to add an event!");
        return;
      }

      const formData = new FormData(form);
      formData.append("lat", lastLat);
      formData.append("lng", lastLng);

      fetch("/save_event", {
        method: "POST",
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          alert("Saved!");
          form.reset();
          modal.classList.add("hidden");
          pinPlaced = false;
        });
    });
  } else {
    console.warn("Form with ID 'eventForm' not found!");
  }
});
