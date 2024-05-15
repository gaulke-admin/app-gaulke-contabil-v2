function displayModal(element){
    let modal_name = element.getAttribute("data-modal-name");
    console.log(modal_name)
    document.querySelector(`[data-modal="${modal_name}"]`).classList.toggle("active");
}

function displayModal_PendenciesIR(element){

    let arr_rows_pendencies = [];
    let modal_name = element.getAttribute("data-modal-name");

    console.log(modal_name)
    console.log(data_pend_IR)
    document.querySelector(`[data-modal="${modal_name}"]`).classList.toggle("active");

    for(let i in data_pend_IR){
        arr_rows_pendencies.push(`
            <tr>
                <td>${data_pend_IR[i]["cod_sistema"]}</td>
                <td>${data_pend_IR[i]["contribuinte"]}</td>
                <td>${data_pend_IR[i]["cpf_cnpj"]}</td>
                <td>${data_pend_IR[i]["celular"]}</td>
                <td>${data_pend_IR[i]["telefone"]}</td>
                <td>${data_pend_IR[i]["ano"]}</td>
                <td>${data_pend_IR[i]["valor_ano_anterior"]}</td>
                <td>${data_pend_IR[i]["valor_ano_atual"]}</td>
                <td>
                    <i class="fa-regular fa-pen-to-square" data-client-id="${data_pend_IR[i]["id_table_CLIENT"]}" data-delivery-id="${data_pend_IR[i]["id_table_IR"]}"></i>
                </td>
            </tr>
        `);
    }

    document.querySelector("#table-pendencies-IR tbody").innerHTML = arr_rows_pendencies.join("");
}
function closeModal_PendenciesIR(element){
    let modal_name = element.getAttribute("data-modal-name");
    document.querySelector(`[data-modal="${modal_name}"]`).classList.remove("active");
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