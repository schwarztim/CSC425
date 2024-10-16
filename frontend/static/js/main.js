document.addEventListener("DOMContentLoaded", function() {
    const bookingForm = document.getElementById('booking-form');
    const availableSlotsContainer = document.getElementById('time-slots');

    const BACKEND_BOOK_URL = 'http://127.0.0.1:5000';  // Set the backend URL explicitly for booking

    function fetchAvailableSlots(date) {
        console.log(`Fetching available slots for date: ${date}`);
        fetch(`/available-slots?date=${date}`)  // Keep fetch as before for available slots
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Available slots data:', data);
                availableSlotsContainer.innerHTML = ''; // Clear previous slots
                data.forEach(slot => {
                    const slotElement = document.createElement('div');
                    slotElement.textContent = slot.time; // Assuming slot object has a 'time' property
                    slotElement.className = 'time-slot';
                    if (slot.booked) {
                        slotElement.classList.add('booked');
                    } else {
                        slotElement.addEventListener('click', () => selectSlot(slot.time, slotElement)); // Pass slot.time for selection
                    }
                    availableSlotsContainer.appendChild(slotElement);
                });
            })
            .catch(error => {
                console.error('Error fetching available slots:', error);
            });
    }

    function selectSlot(slot, slotElement) {
        const selectedSlotInput = document.getElementById('selected-time');
        selectedSlotInput.value = slot; // Set selected slot time value (HH:MM)

        const currentlySelected = document.querySelector('.time-slot.selected');
        if (currentlySelected) {
            currentlySelected.classList.remove('selected');
        }
        slotElement.classList.add('selected');
    }

    bookingForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Extract form data directly from form elements
        const selectedSlot = document.getElementById('selected-time').value;  // Time (HH:MM)
        const name = document.getElementById('name').value;
        const phoneNumber = document.getElementById('phone').value;
        const selectedDate = document.getElementById('date').value;  // Date (YYYY-MM-DD)

        if (!selectedSlot || !name || !phoneNumber || !selectedDate) {
            alert('Date, time slot, name, and phone number are required.');
            return;
        }

        // Construct the correct JSON payload
        const requestData = { 
            time: selectedSlot, 
            date: selectedDate, 
            name: name, 
            phone_number: phoneNumber 
        };  
        console.log('Booking request data:', requestData);

        // Send the booking request to the backend
        fetch(`${BACKEND_BOOK_URL}/book`, {  // Use backend URL only for booking
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Booking response data:', data);
            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                alert('Booking successful!');
                fetchAvailableSlots(selectedDate);  // Refresh available slots after successful booking
            }
        })
        .catch(error => {
            console.error('Error booking time:', error);
            alert('Error booking time');
        });
    });

    document.getElementById('date').addEventListener('change', function(event) {
        const selectedDate = event.target.value;
        fetchAvailableSlots(selectedDate);
    });

    // Initial fetch for today’s date or any default date
    fetchAvailableSlots(new Date().toISOString().split('T')[0]);
});
