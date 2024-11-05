function applyFilters() {
    const selectedTypes = Array.from(document.querySelectorAll("input[name='car-type']:checked")).map(cb => cb.value);
    const selectedFuels = Array.from(document.querySelectorAll("input[name='fuel-type']:checked")).map(cb => cb.value);
    const selectedSeats = Array.from(document.querySelectorAll("input[name='seats']:checked")).map(cb => cb.value);

    const cars = document.querySelectorAll('.car-card');

    cars.forEach(car => {
        const carType = car.getAttribute('data-type');
        const carFuel = car.getAttribute('data-fuel');
        const carSeats = car.getAttribute('data-seats');

        const typeMatch = selectedTypes.length === 0 || selectedTypes.includes(carType);
        const fuelMatch = selectedFuels.length === 0 || selectedFuels.includes(carFuel);
        const seatsMatch = selectedSeats.length === 0 || selectedSeats.includes(carSeats);

        // Display or hide the car card based on filter match
        car.style.display = (typeMatch && fuelMatch && seatsMatch) ? "block" : "none";
    });
}

// Function to handle single selection across all price options
function handlePriceOptionSelection() {
    document.querySelectorAll('.price-option').forEach(option => {
        option.addEventListener('click', function () {
            const isSelected = option.classList.contains('selected');

            // Remove 'selected' class from all options
            document.querySelectorAll('.price-option').forEach(opt => opt.classList.remove('selected'));

            // Add 'selected' class to clicked option if it wasn't selected before
            if (!isSelected) {
                option.classList.add('selected');
            }
        });
    });
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', handlePriceOptionSelection);
