/**
 * This file handles the “Save Recipe” AJAX functionality
 */

document.addEventListener("DOMContentLoaded", () => {
    const token = document.querySelector('meta[name="csrf-token"]').content;

    // Save Recipe Button.
    document.querySelectorAll(".save-recipe-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const url = btn.dataset.url;
            if (!url) {
                console.error("save-recipe-btn missing data-url");
                return;
            }

            btn.disabled = true;
            btn.textContent = "Saving…";

            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": token,
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({})
            })
            .then(res => {
                if (!res.ok) throw new Error("Network response was not OK");
                return res.json();
            })
            .then(data => {
                if (data.status === "ok") {
                    btn.textContent = "Saved!";
                } else {
                    btn.textContent = "Error";
                    btn.disabled = false;
                }
            })
            .catch(err => {
                console.error("Save Recipe AJAX error:", err);
                btn.textContent = "Error";
                btn.disabled = false;
            });
        });
    });

    
    // Add Missing to Grocery Button.
    document.querySelectorAll(".add-missing-btn").forEach(btn => {
      btn.addEventListener("click", event => {
        event.preventDefault();
        event.stopPropagation();

        const form = btn.closest("form");
        const url = btn.dataset.url;

        if (!url) {
          console.error("add-missing-btn missing data-url");
          return;
        }

        btn.disabled = true;
        btn.textContent = "Adding…";

        const formData = new FormData(form);
        const items = formData.getAll("food_name");
        const quantities = formData.getAll("quantity");
        const categories = formData.getAll("category");
        const next = formData.get("next");

        console.log("Items:", items);
        console.log("Quantities:", quantities);
        console.log("Categories:", categories);

        if (!items.length || !quantities.length || !categories.length) {
          console.error("Missing items/quantities/categories");
          btn.textContent = "Error";
          btn.disabled = false;
          return;
        }

        fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": token,
            "X-Requested-With": "XMLHttpRequest"
          },
          body: JSON.stringify({ items, quantities, categories, next: next })
        })
        .then(res => {
          if (!res.ok) throw new Error("Network response was not OK");
          return res.json();
        })
        .then(data => {
          if (data.status === "ok") {
            btn.textContent = "Added!";
          } else {
            throw new Error(data.message || "Server error");
          }
        })
        .catch(err => {
          console.error("Add Missing to Grocery AJAX error:", err);
          btn.textContent = "Error";
          btn.disabled = false;
        });
      });
    });
});
