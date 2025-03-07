function toggleSortIcon(thElement, asc) {
    let allSortIcons = document.querySelectorAll('.search_sort_icon')
    allSortIcons.forEach(icon => icon.style.display = 'none')
    let sortStyle = asc ? 'asc' : 'desc'
    console.log(thElement)
    let sortIcon = thElement.querySelector(`svg[id$='${sortStyle}_icon']`)
    console.log(sortIcon)
    sortIcon.style.display = 'inline'
}

// Sorting logic is from this answer https://stackoverflow.com/a/49041392, modified slightly to insert into tbody

const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

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

            // Try converting dates to numbers first
            let parsedDateVar1 = Date.parse(rawVar1)
            let parsedDateVar2 = Date.parse(rawVar2)

            let var1
            let var2

            if (isNaN(parsedDateVar1) || isNaN(parsedDateVar2)) {  // at least one value is not a valid date 
                var1 = rawVar1
                var2 = rawVar2 
            } else {  // Both are valid dates, so we can use their numerical forms
                var1 = parsedDateVar1
                var2 = parsedDateVar2
            }

            return (var1 !== '' && var2 !== '' && !isNaN(var1) && !isNaN(var2))  // if values are numeric
                ? var1 - var2  // numeric comparison
                : var1.toString().localeCompare(var2);  // localeCompare for string comparison
        }(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));
    }
};

function addListenersToTableHeaders() {
    document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
        let table = th.closest('table')
        let tableBody = table.querySelector('tbody')
        toggleSortIcon(th, this.asc)
        Array.from(tableBody.querySelectorAll('tr'))
            .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
            .forEach(tr => tableBody.appendChild(tr) )
    })))
}

addListenersToTableHeaders()