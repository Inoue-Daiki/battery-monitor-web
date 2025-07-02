document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/summary")
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById("cardContainer");
      data.forEach(device => {
        const card = document.createElement("div");
        card.className = "card";
        card.onclick = () => window.location.href = `/device/${device.device_name}`;

        const battery = document.createElement("div");
        battery.className = "battery";
        const level = document.createElement("div");
        level.className = "battery-level";
        level.style.width = (device.level * 100) + "%";
        if (device.level < 0.3) level.style.backgroundColor = "#f44336";
        else if (device.level < 0.8) level.style.backgroundColor = "#ffc107";
        battery.appendChild(level);

        card.appendChild(battery);
        card.innerHTML += `<strong>${device.device_name}</strong><br>残量：${Math.round(device.level * 100)}% ${device.charging ? "（充電中）" : "（放電中）"}`;
        container.appendChild(card);
      });
    });
});
