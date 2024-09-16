// This import is effectively done for us in the HTML, by adding it in </script> tags in main.html 
// import { reapplyEveryOtherRowCss } from reapply_table_css

const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
    v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

// do the work...
document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
    let table = th.closest('table')
    let tableBody = table.querySelector('tbody')
    Array.from(tableBody.querySelectorAll('tr'))
        .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
        .forEach(tr => tableBody.appendChild(tr) )
    reapplyEveryOtherRowCss(table.id)
})))