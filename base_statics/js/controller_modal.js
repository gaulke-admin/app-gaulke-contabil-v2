function displayModal(element){
    let modal_name = element.getAttribute("data-modal-name");
    console.log(modal_name)
    document.querySelector(`[data-modal="${modal_name}"]`).classList.toggle("active");
}

function displayModalByID(element){
    let modal_name = element.id
    document.querySelector(`[data-modal="${modal_name}"]`).classList.toggle("active");
}
function displayModalDeleteIR(element){
    let modal_name = element.getAttribute("data-modal-name");

    let id_table_IR     = element.getAttribute("data-row-delete");
    let contribuinte    = element.getAttribute("data-row-contribuinte");
    let ano             = element.getAttribute("data-row-ano");
    let status_smart_IR = element.getAttribute("data-row-status_smart_IR");

    document.querySelector('[data-info-modal="info-row-contribuinte"]').textContent = contribuinte;
    document.querySelector('[data-info-modal="info-row-ano"]').textContent = ano;
    document.querySelector('[data-info-modal="info-row-status_smart_IR"]').textContent = status_smart_IR;

    document.querySelector(`[data-modal="${modal_name}"]`).classList.toggle("active");
    document.querySelector(`[data-modal="${modal_name}"]`).querySelectorAll("[data-row-delete")[0].setAttribute("data-row-delete", id_table_IR);
}
function displayModalDeleteClient(element){

    let modal_name = element.getAttribute("data-modal-name");

    let id_table_client     = element.getAttribute("data-row-delete");
    let cpf             = element.getAttribute("data-row-cpf");
    let contribuinte    = element.getAttribute("data-row-contribuinte");

  

    document.querySelector('[data-info-modal="info-row-client-cpf"]').textContent = cpf;
    document.querySelector('[data-info-modal="info-row-client-contribuinte"]').textContent = contribuinte;


    document.querySelector(`[data-modal="${modal_name}"]`).classList.toggle("active");
    document.querySelector(`[data-modal="${modal_name}"]`).querySelectorAll("[data-row-delete")[0].setAttribute("data-row-delete", id_table_client);
}