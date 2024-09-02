// main.js

window.onload = function () {
    // Initialize date pickers
    $(".date-picker").datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        maxDate: new Date() // Prevent future dates
    });

    // Event listener for the "Load Data" button
    document.getElementById('loadData').addEventListener('click', function () {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;

        if (!startDate || !endDate) {
            alert('Please select both start and end dates.');
            return;
        }


        const tableBody = document.getElementById('tableBody');
        tableBody.innerHTML = `                    <tr class="loading">
                        <td colspan="8" class="spinner-cell">
                            <div class="spinner-container">
                               
                                <div class="spinner"></div>
                            </div>
                        </td>
                    </tr>`; 


        showSpinner();

        fetchData(startDate, endDate);
    });

   document.getElementById('tableBody').addEventListener('click', function (event) {
    if (event.target && event.target.classList.contains('fetchDataBtn')) {
        const clientId = event.target.getAttribute('data-client-id');
        const taskName = event.target.getAttribute('data-task-name');

        const requestData = {
            client_id: clientId,
            task_name: taskName
        };

        // Fetch breakdown data via AJAX
        fetch('/api/get-breakdown-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            populateBreakdownTable(data); // Populate the modal table
            document.getElementById("myModal").style.display = "block"; // Show the modal
        })
        .catch(error => console.error('Error fetching breakdown data:', error));
    };


    if (event.target && event.target.classList.contains('fetchDataBtn_email')) {
        const clientId = event.target.getAttribute('data-client-id');
        const taskName = event.target.getAttribute('data-task-name');

        const requestData = {
            client_id: clientId,
            task_name: taskName
        };

        // Fetch breakdown data via AJAX
        fetch('/api/get-breakdown-data_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            populateBreakdownTable(data); // Populate the modal table
            document.getElementById("myModal").style.display = "block"; // Show the modal
        })
        .catch(error => console.error('Error fetching breakdown data:', error));
    }


});

    // Close modal when close button is clicked
    document.querySelector('.close').addEventListener('click', function () {
        document.getElementById("myModal").style.display = "none";
    });

    // Close modal when clicking outside of it
    window.addEventListener('click', function (event) {
        if (event.target === document.getElementById("myModal")) {
            document.getElementById("myModal").style.display = "none";
        }
    });

    var startDate = '2022-08-01';
    var endDate = '2023-08-30';
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    // Set default values in date inputs
    startDateInput.value = startDate;
    endDateInput.value = endDate;
    fetchData(startDate, endDate);
    const loadingRow = document.querySelector('.loading'); 
    // Function to show the loading spinner
    function showSpinner() {
        loadingRow.style.display = 'table-row'; 
    }

    // Function to hide the loading spinner
    function hideSpinner() {
        loadingRow.style.display = 'none'; // Hide the loading spinner row
    }

};

// Fetch data based on selected date range
async function fetchData(startDate, endDate) {
    
    try {
        const response = await fetch(`/api/clients-data?start_date=${startDate}&end_date=${endDate}`);
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        const data = await response.json();
        populateTable(data);
    } catch (error) {
        console.error('Failed to fetch data:', error);
        showErrorMessage();
    }
}

// Populate the table with the fetched data
function populateTable(data) {
    const tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = ``; // Clear existing content

    // Check if there's data to display
    if (!data.length) {
        tableBody.innerHTML = '<tr class="loading"><td colspan="2">No data available</td></tr>';
        return;
    }

    // Add rows dynamically based on fetched data
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${row.client}</td><td>${row.cost} $</td><td>    <button id="fetchDataBtnx" 
    data-client-id="${row.client}"  
    class="fetchDataBtn btn btn-info mt-3">Handler-wise-Breakdown</button></td><td>    <button id="fetchDataBtnx" 
    data-client-id="${row.client}"  
    class="fetchDataBtn_email btn btn-info mt-3">Email-wise-Breakdown</button></td>`;
        tableBody.appendChild(tr);
    });

    // Initialize DataTable or update existing one
    if ($.fn.DataTable.isDataTable('#clientTable')) {
        $('#clientTable').DataTable().clear().rows.add($(tableBody).find('tr')).draw();
    } else {
        $('#clientTable').DataTable({
            paging: true,
            searching: true,
            info: true,
            responsive: true,
            destroy: true,
            order: [[1, 'desc']] // Allows reinitialization with new data
        });
    }

    // Remove loading message
    document.querySelector('.loading')?.remove();
}

// Show error message if fetching data fails
function showErrorMessage() {
    const tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = '<tr class="error-message"><td colspan="2">Error fetching data. Please try again later.</td></tr>';
}

// Populate the modal table with breakdown data
function populateBreakdownTable(data) {
    const tableBody = document.getElementById("breakdownTableBody");
    tableBody.innerHTML = ''; // Clear existing rows

    // Parse and display the hierarchical breakdown data
    for (const [taskName, subTasks] of Object.entries(data)) {
        // #console.log(data)
        for (const [subTaskName, details] of Object.entries(subTasks)) {
            for (const [name, info] of Object.entries(details)) {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${String(subTaskName)}</td>
                    <td>${String(name)}</td>
                    <td>$${info.cost}</td>
                    <td>${info.mssg_count}</td>
                `;
                tableBody.appendChild(row);
            }
        }
    }


    // Initialize DataTable or update existing one
    if ($.fn.DataTable.isDataTable('#dataTable')) {
        $('#dataTable').DataTable().clear().rows.add($(tableBody).find('tr')).draw();
    } else {
        $('#dataTable').DataTable({
            paging: true,
            searching: true,
            info: true,
            responsive: true,
            destroy: true // Allows reinitialization with new data



        });
    }





}





