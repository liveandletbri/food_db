let addTimingButton = document.querySelector("#add-timing-form")
let deleteTimingButton = document.querySelector("#delete-timing-form")
let timingTable = document.querySelector("#timing-table")

function addTimingRow() {
    let rows = timingTable.rows
    let lastRow = rows[rows.length - 1]
    let newRow = lastRow.cloneNode(true)
    
    // Update row index
    let newIndex = rows.length - 1
    newRow.setAttribute('name', `timing_${newIndex}_row`)
    
    // Update input IDs and names
    let typeSelect = newRow.querySelector('select[name^="timing_"]')
    let minutesInput = newRow.querySelector('input[name^="timing_"]')
    
    if (typeSelect) {
        typeSelect.setAttribute('id', `id_timing_${newIndex}_type`)
        typeSelect.setAttribute('name', `timing_${newIndex}_type`)
        typeSelect.value = '' // Clear the value
    }
    
    if (minutesInput) {
        minutesInput.setAttribute('id', `id_timing_${newIndex}_minutes`)
        minutesInput.setAttribute('name', `timing_${newIndex}_minutes`)
        minutesInput.value = '' // Clear the value
    }
    
    // Update delete button
    let deleteButton = newRow.querySelector('.delete_timing_button')
    if (deleteButton) {
        deleteButton.onclick = function() { deleteTimingRow(this) }
    }
    
    timingTable.appendChild(newRow)
    updateTimingCount()
}

function deleteTimingRow(button) {
    let row = button.closest('tr')
    row.remove()
    updateTimingCount()
    renumberTimingRows()
}

function renumberTimingRows() {
    let rows = Array.from(timingTable.rows).slice(1) // Skip header row
    rows.forEach(function(row, index) {
        row.setAttribute('name', `timing_${index}_row`)
        
        let typeSelect = row.querySelector('select[name^="timing_"]')
        let minutesInput = row.querySelector('input[name^="timing_"]')
        
        if (typeSelect) {
            typeSelect.setAttribute('id', `id_timing_${index}_type`)
            typeSelect.setAttribute('name', `timing_${index}_type`)
        }
        
        if (minutesInput) {
            minutesInput.setAttribute('id', `id_timing_${index}_minutes`)
            minutesInput.setAttribute('name', `timing_${index}_minutes`)
        }
    })
}

function updateTimingCount() {
    let count = timingTable.rows.length - 1 // Subtract header row
    document.getElementById('id_extra_timing_count').value = Math.max(0, count - 1)
}

function deleteLastTiming() {
    let rows = timingTable.rows
    if (rows.length > 2) { // Keep at least header + 1 data row
        timingTable.deleteRow(rows.length - 1)
        updateTimingCount()
    }
}

if (addTimingButton) {
    addTimingButton.addEventListener('click', addTimingRow)
}

if (deleteTimingButton) {
    deleteTimingButton.addEventListener('click', deleteLastTiming)
}

// Initialize delete buttons on existing rows
document.addEventListener('DOMContentLoaded', function() {
    let deleteButtons = document.querySelectorAll('.delete_timing_button')
    deleteButtons.forEach(function(button) {
        button.onclick = function() { deleteTimingRow(this) }
    })
})
