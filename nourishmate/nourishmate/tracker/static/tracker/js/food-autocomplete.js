/**
 * This file listens for food input, fetches nutrition data via AJAX,
 * and auto-fills the nutrition fields as a user types.
 */

document.addEventListener("DOMContentLoaded", function () {

    function autofillNutrition(ingredientId) {
        const quantity = document.querySelector('#id_quantity_amount')?.value;
        const unit = document.querySelector('#id_quantity_unit')?.value;
    
        if (!ingredientId || !quantity || !unit || unit === '') return;
    
        fetch(`/api/nutrition/?id=${ingredientId}&amount=${quantity}&unit=${unit}`)
            .then(res => res.json())
            .then(data => {
                for (const [key, value] of Object.entries(data)) {
                    const input = document.querySelector(`#id_${key}`);
                    if (input) input.value = value;
                }
            });
    }
    
    const foodInput = document.querySelector('#id_food_name');
    let timeout = null;
    let fetchedOptions = [];
    let ingredientId = null;

    if (foodInput) {
        foodInput.setAttribute("list", "food-suggestions");

        foodInput.addEventListener("input", function () {
            clearTimeout(timeout);
            ingredientId = null;
            const query = this.value;

            if (query.length < 2) return;

            timeout = setTimeout(() => {
                fetch(`/api/autocomplete/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        fetchedOptions = data;  

                        const datalist = document.getElementById("food-suggestions");
                        if (!datalist) return;

                        datalist.innerHTML = "";
                        data.forEach(item => {
                            const option = document.createElement("option");
                            option.value = item.name;
                            option.setAttribute("data-id", item.id);
                            datalist.appendChild(option);
                        });
                    });
            }, 300);
        });

        foodInput.addEventListener("change", function () {
            const inputValue = this.value.toLowerCase();
        
            const proceedWithMatch = () => {
                const match = fetchedOptions.find(
                    item => item.name.toLowerCase() === inputValue
                );
        
                console.log("🍞 Input value:", inputValue);
                console.log("🔍 Matched object:", match);
        
                if (!match) {
                    console.warn("⚠️ No matching result found in cached list for:", inputValue);
                    return;
                }
        
                ingredientId = match.id;
                console.log("Selected ingredient:", match.name, "ID:", ingredientId);
        
                const quantityInput = document.querySelector('#id_quantity_amount');
                const unitSelect = document.querySelector('#id_quantity_unit');
        
                autofillNutrition(ingredientId); 

                quantityInput?.addEventListener("input", () => setTimeout(() => autofillNutrition(ingredientId), 500));
                unitSelect?.addEventListener("change", () => setTimeout(() => autofillNutrition(ingredientId), 500));

            };
        
            if (fetchedOptions.length === 0 && inputValue.length >= 2) {
                fetch(`/api/autocomplete/?q=${encodeURIComponent(inputValue)}`)
                    .then(response => response.json())
                    .then(data => {
                        fetchedOptions = data;
                        proceedWithMatch();
                    });
            } else {
                proceedWithMatch();
            }
        });
    }

    document.querySelector('#id_quantity_amount')?.addEventListener("input", () => {
        if (ingredientId) autofillNutrition(ingredientId);
    });

    document.querySelector('#id_quantity_unit')?.addEventListener("change", () => {
        if (ingredientId) autofillNutrition(ingredientId);
    });
});