const makeEditFormVisible = () => {
    const editForm = document.getElementById('edit-form');
    editForm.classList.remove('d-none');
};

const showFormButton = document.getElementById('show-form-button');
showFormButton.addEventListener('click', makeEditFormVisible);

const formErrors = document.querySelector('[role=alert]');
if (formErrors) {
    const event = new Event("click");
    showFormButton.dispatchEvent(event)
};
