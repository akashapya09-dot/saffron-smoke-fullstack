const API_BASE_URL = (window.API_BASE_URL || "http://BACKEND_PUBLIC_IP:8000").replace(/\/$/, "");

const fallbackDishes = [
{id:1,name:"Charred Paneer Tikka",category:"Small plates",price:280,rating:"4.9",image:"https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=900&q=85",description:"Smoky paneer, house spices, mint chutney and a squeeze of lime."},
{id:2,name:"Fire-Roasted Pizza",category:"Mains",price:390,rating:"4.8",image:"https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?auto=format&fit=crop&w=900&q=85",description:"Crisp edges, slow-roasted tomato, basil and creamy mozzarella."},
{id:3,name:"Saffron Butter Chicken",category:"Mains",price:420,rating:"5.0",image:"https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=900&q=85",description:"A rich, silky tomato gravy finished with cream and fragrant spices."},
{id:4,name:"Garden Burrata Salad",category:"Small plates",price:310,rating:"4.7",image:"https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=85",description:"Seasonal greens, juicy tomatoes, herbs and a bright citrus dressing."},
{id:5,name:"Truffle Mushroom Pasta",category:"Mains",price:360,rating:"4.9",image:"https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=900&q=85",description:"Silky pasta, golden mushrooms, parmesan and a hint of truffle."},
{id:6,name:"Chocolate Lava Cake",category:"Desserts",price:240,rating:"4.9",image:"https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=85",description:"Warm chocolate cake with a molten centre and vanilla cream."},
{id:7,name:"Berry Cheesecake",category:"Desserts",price:260,rating:"4.8",image:"https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=900&q=85",description:"Creamy cheesecake, berry compote and a buttery biscuit base."},
{id:8,name:"Mango Mint Cooler",category:"Drinks",price:150,rating:"4.7",image:"https://images.unsplash.com/photo-1513558161293-cd2a0e3e3c1c?auto=format&fit=crop&w=900&q=85",description:"Ripe mango, fresh mint and sparkling citrus over ice."},
{id:9,name:"Cold Brew Tonic",category:"Drinks",price:170,rating:"4.8",image:"https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=900&q=85",description:"Slow-steeped coffee, bright citrus and a crisp tonic finish."}
];

const grid = document.getElementById("dish-grid");
const search = document.getElementById("search");
const toast = document.getElementById("toast");
let dishes = [...fallbackDishes];
let category = "All";
const cart = new Map();
let toastTimer;

function notify(text) {
  toast.textContent = text;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2800);
}

async function loadMenu() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/menu`, {headers: {"Accept": "application/json"}});
    if (!response.ok) throw new Error(`Menu API returned ${response.status}`);
    const data = await response.json();
    if (Array.isArray(data.items) && data.items.length) {
      dishes = data.items;
      renderMenu();
      notify("Menu loaded from the restaurant backend");
    }
  } catch (error) {
    console.warn("Backend menu unavailable; showing built-in demo menu.", error);
    renderMenu();
    notify("Demo menu loaded — backend connection not available yet");
  }
}

function renderMenu() {
  const q = search.value.trim().toLowerCase();
  const visible = dishes.filter(d =>
    (category === "All" || d.category === category) &&
    (`${d.name} ${d.description} ${d.category}`).toLowerCase().includes(q)
  );

  if (!visible.length) {
    grid.innerHTML = "<p>No dishes found. Try another search.</p>";
    return;
  }

  grid.innerHTML = visible.map(d => `
    <article class="dish-card">
      <div class="dish-photo">
        <img src="${d.image}" alt="${d.name}" loading="lazy"
          onerror="this.onerror=null;this.src='https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80'">
        <span class="dish-tag">${d.category}</span>
      </div>
      <div class="dish-info">
        <div class="dish-title-row"><h3>${d.name}</h3><span class="dish-price">₹${d.price}</span></div>
        <p>${d.description}</p>
        <div class="dish-footer">
          <span class="dish-rating">★ ${d.rating} &nbsp; · &nbsp; Chef's pick</span>
          <button class="add-button" data-id="${d.id}">${cart.get(d.id) ? "Added (" + cart.get(d.id) + ")" : "+ Add"}</button>
        </div>
      </div>
    </article>`).join("");

  grid.querySelectorAll(".add-button").forEach(button => {
    button.addEventListener("click", async () => {
      const id = Number(button.dataset.id);
      const dish = dishes.find(item => Number(item.id) === id);
      if (!dish) return;
      cart.set(id, (cart.get(id) || 0) + 1);
      renderMenu();

      try {
        const response = await fetch(`${API_BASE_URL}/api/cart-events`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({dish_id: id, quantity: 1})
        });
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        notify(`Added ${dish.name} to your order · saved by backend`);
      } catch (error) {
        console.warn("Could not record cart action on backend.", error);
        notify(`Added ${dish.name} to your order · local demo only`);
      }
    });
  });
}

document.querySelectorAll(".filter").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelector(".filter.active")?.classList.remove("active");
    button.classList.add("active");
    category = button.dataset.category;
    renderMenu();
  });
});

search.addEventListener("input", renderMenu);
renderMenu();
loadMenu();


// Full-stack reservation request: validated and persisted by the Flask/SQLite backend.
const reservationDateInput = document.getElementById("reservation-date");
const reservationForm = document.getElementById("reservation-form");
const reservationStatus = document.getElementById("reservation-status");
if (reservationDateInput) {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  reservationDateInput.min = tomorrow.toISOString().slice(0, 10);
}
reservationForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = reservationForm.querySelector('button[type="submit"]');
  const fields = new FormData(reservationForm);
  const payload = {
    name: String(fields.get("name") || "").trim(),
    email: String(fields.get("email") || "").trim(),
    phone: String(fields.get("phone") || "").trim(),
    guests: Number(fields.get("guests")),
    date: String(fields.get("date") || ""),
    time: String(fields.get("time") || ""),
    notes: String(fields.get("notes") || "").trim()
  };
  reservationStatus.className = "reservation-status";
  reservationStatus.textContent = "Sending your reservation request…";
  button.disabled = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/reservations`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || `Request failed (${response.status})`);
    reservationStatus.className = "reservation-status success";
    reservationStatus.textContent = `Reservation request saved! Your reference is ${result.reference}. This is a request, not a confirmed table assignment; staff must confirm it.`;
    reservationForm.reset();
    if (reservationDateInput) {
      const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1);
      reservationDateInput.min = tomorrow.toISOString().slice(0, 10);
    }
    notify("Reservation request saved successfully");
  } catch (error) {
    reservationStatus.className = "reservation-status error";
    reservationStatus.textContent = `Could not save the request: ${error.message}. Check the backend connection and try again.`;
  } finally {
    button.disabled = false;
  }
});
