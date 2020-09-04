const showOptions = (event) => {
    makeOptionActive(event.currentTarget.value)
};

const makeOptionActive = (name) => {
    const previousContainer = document.getElementById(
        LastActiveFilterName
    );
    if (previousContainer) {
        previousContainer.setAttribute('hidden', '');
    };

    const container = document.getElementById(name);
    if (container) {
        container.removeAttribute('hidden');
    };

    LastActiveFilterName = name;
};

const select_ = document.getElementById('id_filter_');
let LastActiveFilterName = select_.value;

makeOptionActive(LastActiveFilterName);

select_.addEventListener("change", showOptions);
