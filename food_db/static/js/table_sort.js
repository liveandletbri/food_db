function toggleSortIcon(thElement, asc) {
    let table = thElement.closest('table')
    let allSortIcons = table.querySelectorAll('.table_sort_icon')
    allSortIcons.forEach(icon => icon.style.display = 'none')
    let sortStyle = asc ? 'asc' : 'desc'
    console.log(thElement)
    let sortIcon = thElement.querySelector(`svg[id$='${sortStyle}_icon']`)
    console.log(sortIcon)
    sortIcon.style.display = 'inline'
}

// Sorting logic is from this answer https://stackoverflow.com/a/49041392, modified slightly to insert into tbody

const getCellValue = (tr, idx) => tr.children[idx].getAttribute('value') || tr.children[idx].textContent;

// Returns a function responsible for sorting a specific column index 
// (idx = columnIndex, asc = ascending order?).
var comparer = function(idx, asc) { 

    // This is used by the array.sort() function...
    return function(a, b) { 

        // This is a transient function, that is called straight away. 
        // It allows passing in different order of args, based on 
        // the ascending/descending order.
        return function(rawVar1, rawVar2) {

            // Sort based on subtraction or localeCompare, based on type.
            // Comparisons return a positive number if var1 is larger/later than var2,
            // negative if the opposite, and zero if they are equivalent.

            // Try assuming string is a Date, and converting to numbers first
            let parsedDateVar1 = Date.parse(rawVar1)
            let parsedDateVar2 = Date.parse(rawVar2)

            let var1
            let var2

            if (/^[0-9]+$/.test(rawVar1) && /^[0-9]+$/.test(rawVar2)) {  // Both strings represent integers
                var1 = parseInt(rawVar1)
                var2 = parseInt(rawVar2)
            } else if (Number.isInteger(parsedDateVar1) && Number.isInteger(parsedDateVar2)) {  // Both are valid dates, so we can use their numerical forms
                var1 = parsedDateVar1
                var2 = parsedDateVar2 
            } else {  // at least one value is not a valid integer or date, so treat them as strings
                var1 = rawVar1
                var2 = rawVar2 
            }

            return (var1 !== '' && var2 !== '' && !isNaN(var1) && !isNaN(var2))  // if values are numeric
                ? var1 - var2  // numeric comparison
                : var1.toString().localeCompare(var2);  // localeCompare for string comparison
        }(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));
    }
};

function sortColumn(event) {
    let th = event.target.closest('th');
    let table = th.closest('table')
    let tableBody = table.querySelector('tbody')
    toggleSortIcon(th, th.asc)
    Array.from(tableBody.querySelectorAll('tr:not(.ignore_row)'))
        // Collect all rows
        const rows = Array.from(tableBody.querySelectorAll('tr'));
        // Find the ignore row and its index
        const ignoreRow = rows.find(row => row.classList.contains('ignore_row'));
        const ignoreIndex = ignoreRow ? rows.indexOf(ignoreRow) : -1;

        // Get rows to sort, excluding ignore_row
        const sortableRows = rows.filter(row => !row.classList.contains('ignore_row'));
        const sortedRows = sortableRows.sort(comparer(Array.from(th.parentNode.children).indexOf(th), th.asc = !th.asc));

        // Remove all rows from the table body
        rows.forEach(row => tableBody.removeChild(row));

        // Reinsert rows, preserving ignore_row in its original position
        sortedRows.forEach((row, idx) => {
            if (ignoreRow && idx === ignoreIndex) {
                tableBody.appendChild(ignoreRow);
            }
            tableBody.appendChild(row);
        });
        // If ignoreRow is at the end
        if (ignoreRow && sortedRows.length === ignoreIndex) {
            tableBody.appendChild(ignoreRow);
        }
}

const sortColumnHandler = (event) => sortColumn(event)

function addListenersToTableHeaders() {
    document.querySelectorAll('th').forEach(th => th.addEventListener('click', sortColumnHandler))
}

addListenersToTableHeaders()