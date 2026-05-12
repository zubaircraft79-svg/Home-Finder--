const toggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");
if (toggle && nav) {
  toggle.addEventListener("click", () => nav.classList.toggle("open"));
}

document.querySelectorAll(".toast").forEach((toast) => {
  setTimeout(() => toast.classList.add("fade"), 4500);
});
