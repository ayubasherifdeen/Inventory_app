// Wait for DOM and jQuery to be ready
$(document).ready(function() {
    // jQuery event delegation for Bootstrap 4
    $('#transactionTableBody').on('click', '.view-transaction', function() {
        const saleId = $(this).data('sale-id');
        loadAndShowSaleDetails(saleId);
    });
});


function loadAndShowSaleDetails(saleId) {
    fetch(`/sales/${saleId}/details/`)
        .then(function(response) {
            if (!response.ok) throw new Error('HTTP ' + response.status);
            return response.json();
        })
        .then(function(data) {
            populateModal(data);
        })
        .catch(function(err) {
            console.error('Failed to load sale details:', err);
            alert('Could not load transaction details. Please try again.');
        });
}

function populateModal(data) {
    // Update header info
    document.getElementById("saleDate").textContent = data.sale_date;
    document.getElementById("saleTotal").textContent = data.total_amount;

    // Build items table
    const tbody = document.getElementById("saleItems");
    tbody.innerHTML = "";

    data.items.forEach(function(item) {
        const row = document.createElement("tr");
        row.innerHTML = 
            '<td>' + escapeHtml(item.product_name) + '</td>' +
            '<td class="currency">₵' + item.unit_price + '</td>' +
            '<td>' + item.quantity + '</td>' +
            '<td class="currency">₵' + item.amount + '</td>';
        tbody.appendChild(row);
    });

    // Show modal using Bootstrap 4 jQuery API
    $('#saleModal').modal('show');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}