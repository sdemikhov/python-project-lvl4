const showAssignedTo = (name) => {
    if (my_tasks.checked) {
        assigned_to.setAttribute('disabled', '')
    } else {
        assigned_to.removeAttribute('disabled')
    };
};

const my_tasks = document.getElementById('id_my_tasks');
const assigned_to = document.getElementById('id_assigned_to');

my_tasks.addEventListener("change", showAssignedTo);

const event = new Event("change");
my_tasks.dispatchEvent(event);
