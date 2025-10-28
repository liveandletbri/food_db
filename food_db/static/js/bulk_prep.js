// Initialize row shift functionality for timing table
window.addEventListener('load', function() {
    initializeRowShiftFunctionality('.timing_table_row', '#timing_table tbody');
});

// Add extra event to listeners for column sorts (column sorting defined in table_sort.js)
// As long as this event listener as registered last (after the event listeners in table_sort.js), it should happen after the rows are sorted
const timingTableHideButtonsHandler = () => hideTopAndBottomButtons('.timing_table_row');
document.querySelectorAll('th').forEach(th => th.addEventListener('click', timingTableHideButtonsHandler))