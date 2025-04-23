const apiKey = 'ed410cae4c0343ff9c5b69991267a9ad';

const map = L.map('map').setView([40.7128, -74.0060], 12); // NYC

L.tileLayer(`https://maps.geoapify.com/v1/tile/carto/{z}/{x}/{y}.png?apiKey=${apiKey}`, {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
