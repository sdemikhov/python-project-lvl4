const makeEditFormVisible = () => {
    const editForm = document.getElementById('edit-form');
    editForm.classList.remove('d-none');
};

const showFormButton = document.getElementById('show-form-button');
showFormButton.addEventListener('click', makeEditFormVisible);
