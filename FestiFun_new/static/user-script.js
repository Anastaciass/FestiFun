let lastLat = null;
let lastLng = null;
document.addEventListener('DOMContentLoaded', function () {
  const map = L.map('map').setView([51.4416, 5.4697], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);
  
  // Load existing events
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
          <br>
          <a href="qrcode">
            <button style="margin-top: 8px; padding: 5px 10px; border-radius: 8px;">Buy Ticket</button>
          </a>
        </div>
      `;
      L.marker([parseFloat(evt.lat), parseFloat(evt.lng)])
        .addTo(map)
        .bindPopup(popupContent);
    });
  });
});
