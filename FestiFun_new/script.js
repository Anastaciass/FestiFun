const map = L.map('map').setView([51.505, -0.09], 13); 

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

document.addEventListener("DOMContentLoaded", () => {
  const searchBar = document.getElementById("search-bar");
  const searchInput = document.getElementById("search-input");
  const filterList = document.getElementById("filter-list");

  function populateFilterList(data) {
    filterList.innerHTML = ""; 
    data.forEach(item => {
      const div = document.createElement("div");
      div.textContent = item;
      div.addEventListener("click", () => {
        searchInput.value = item; 
        filterList.style.display = "none"; 
      });
      filterList.appendChild(div);
    });
  }

  function fetchAndUpdateTopics() {
    fetch('http://127.0.0.1:5000/api/topics')
      .then(response => response.json())
      .then(topics => {
        populateFilterList(topics); 
      })
      .catch(error => {
        console.error("Error fetching topics:", error);
      });
  }

  fetchAndUpdateTopics();

  setInterval(fetchAndUpdateTopics, 10000);

  searchBar.addEventListener("click", () => {
    if (filterList.style.display === "none" || filterList.style.display === "") {
      filterList.style.display = "block"; 
    } else {
      filterList.style.display = "none"; 
    }
  });


  document.addEventListener("click", (event) => {
    if (!searchBar.contains(event.target) && !filterList.contains(event.target)) {
      filterList.style.display = "none";
    }
  });


  searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase();
    fetch('http://127.0.0.1:5000/api/topics')
      .then(response => response.json())
      .then(topics => {
        const filteredData = topics.filter(item => item.toLowerCase().includes(query));
        populateFilterList(filteredData);
      })
      .catch(error => {
        console.error("Error fetching topics for filtering:", error);
      });
  });
});
