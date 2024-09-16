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
        return function(v1, v2) {

            // sort based on a numeric or localeCompare, based on type...
            return (v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2)) 
                ? v1 - v2 
                : v1.toString().localeCompare(v2);
        }(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));
    }
};

// do the work...
document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
    let table = th.closest('table')
    let tableBody = table.querySelector('tbody')
    toggleSortIcon(th, this.asc)
    Array.from(tableBody.querySelectorAll('tr'))
        .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
        .forEach(tr => tableBody.appendChild(tr) )
})))