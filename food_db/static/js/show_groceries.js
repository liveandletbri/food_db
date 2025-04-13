let showButton = document.getElementById('show_groceries_button')
let selectTextButton = document.getElementById('select_text_button');
let closeButton = document.getElementById('close_modal_button');
let modal = document.getElementById('grocery_list_modal');
let modalText = document.getElementById('modal_text');

function openModal() {
    modal.style.display = 'block';
}

function closeModal() {
    modal.style.display = 'none';
}

function selectElementText() {
    if (window.getSelection) {
        let selection = window.getSelection();
        selection.removeAllRanges();
        let range = document.createRange();
        range.selectNodeContents(modalText);
        selection.addRange(range);
    } else if (document.selection) {
        let range = document.body.createTextRange();
        range.moveToElementText(modalText);
        range.select();
    }
}

showButton.addEventListener('click', openModal);
closeButton.addEventListener('click', closeModal);
selectTextButton.addEventListener('click', selectElementText);

// Close the modal if the user clicks outside of it
window.addEventListener('click', function(event) {
    if (event.target == modal) {
        closeModal();
    }
});

// Also close on pressing Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' || event.keyCode === 27) {
        closeModal();
    }
  });