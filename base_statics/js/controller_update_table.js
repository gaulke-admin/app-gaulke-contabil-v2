function check_filter(text, text_filter){
    text = String(text).toUpperCase();
    text_filter = String(text_filter).toUpperCase();
    
    if (text.indexOf(text_filter) > -1){
        return true;
    } else {
        return false;
    }
}

function check_filter_in_filters_localSorage(text, filter){
    try {
        if (filter["filter"].length == 0 || filter["filter"].includes("Todos") ){
            return true;
        }
        if (filter["filter"].indexOf(text) > -1){
            return true;
        } else {
            return false;
        }
    } catch (error) {
        return true;
    }
}

function update_values_otions(data){

    for (let i in data) {
            
        let id_table_IR     = data[i]["id_table_IR"];
        let status_pagamento_IR = data[i]["status_pagamento_IR"];

        const getElements = new Promise((resolve, reject)=>{
            let select_elem_status_pagamento_IR = document.getElementById(`status_pagamento_IR-${id_table_IR}`);
            try {
                select_elem_status_pagamento_IR.querySelectorAll("option").forEach((e)=>{
                    if(e.value == status_pagamento_IR){
                        e.selected = true;
                    }
                });
            } catch (error) {};
           
            resolve({
                select_elem_status_pagamento_IR: select_elem_status_pagamento_IR
            });
        });
    }
}

async function update_table_IR(){
    
    let arr_elements_tr = new Array();

    let text_filter = document.getElementById("text_filter").value;
    let table = document.querySelector(`[data-table-name="table-indo-JB-SMART-IR"]`);

    table.querySelector("tbody").innerHTML = "<tbody></tbody>";

    // console.log(" ------------- data_table_deliveries_IR ------------- ")
    // console.log(data_table_deliveries_IR)
    let data = data_table_deliveries_IR["data"];

    let cont_row = 0;
    let limit_rows = 40000;
    let filter_localStorage_status_pagamento = await JSON.parse(window.localStorage.getItem("status_pagamento")); //["filter"];
    let filter_localStorage_status_smart_IR = await JSON.parse(window.localStorage.getItem("status_smart_IR")); //["filter"];

    const updateTable = new Promise((resolve, reject)=>{
        for (let i in data) {
            if(cont_row < limit_rows){
                let id_table_IR             = data[i]["id_table_IR"];
                let ano                     = data[i]["ano"];
                let celular                 = data[i]["celular"];
                let cod_sistema             = data[i]["cod_sistema"];
                let contribuinte            = data[i]["contribuinte"];
                let cpf_cnpj                = data[i]["cpf_cnpj"];
                let dificuldade             = data[i]["dificuldade"];
                let telefone                = data[i]["telefone"];
                let valor_ano_anterior      = data[i]["valor_ano_anterior"];

                let valor_ano_atual         = data[i]["valor_ano_atual"];
                let dt_pagamento_IR         = data[i]["dt_pagamento_IR"];
                
                let status_smart_IR         = data[i]["status_smart_IR"];
                let status_pagamento_IR     = data[i]["status_pagamento_IR"];
                let info_forma_pagamento    = data[i]["info_forma_pagamento"];
                // ----
                let tt_comments   = data[i]["tt_comments"];

                let check_id_table_IR           = check_filter(id_table_IR, text_filter);
                let check_ano                   = check_filter(ano, text_filter);
                let check_celular               = check_filter(celular, text_filter);
                let check_cod_sistema           = check_filter(cod_sistema, text_filter);
                let check_contribuinte          = check_filter(contribuinte, text_filter);
                let check_cpf_cnpj              = check_filter(cpf_cnpj, text_filter);
                let check_dificuldade           = check_filter(dificuldade, text_filter);
                let check_telefone              = check_filter(telefone, text_filter);
                let check_valor_ano_anterior    = check_filter(valor_ano_anterior, text_filter);
                let check_valor_ano_atual       = check_filter(valor_ano_atual, text_filter);
                let check_dt_pagamento_IR       = check_filter(dt_pagamento_IR, text_filter);
                
                let check_status_smart_IR       = check_filter(status_smart_IR, text_filter);
                let check_status_pagamento_IR   = check_filter(status_pagamento_IR, text_filter);
                // ------------------------------------------------------------------------------
                let check_filter_status_smart_IR        = check_filter_in_filters_localSorage(status_smart_IR, filter_localStorage_status_smart_IR);
                let check_filter_status_pagamento_IR    = check_filter_in_filters_localSorage(status_pagamento_IR, filter_localStorage_status_pagamento);
                
                // ----
                let check_tt_comments = check_filter(tt_comments, text_filter);
                
                if(check_id_table_IR
                    || check_ano
                    || check_celular
                    || check_cod_sistema
                    || check_contribuinte
                    || check_cpf_cnpj
                    || check_dificuldade
                    || check_tt_comments
                    || check_telefone
                    || check_valor_ano_anterior
                    || check_valor_ano_atual
                    || check_dt_pagamento_IR
                    
                    || check_status_smart_IR
                    || check_status_pagamento_IR
                ) {
                    
                    if (check_filter_status_smart_IR && check_filter_status_pagamento_IR){


                        arr_elements_tr.push(`
                            <tr data-row-table-IR="${id_table_IR}">
                                <td>
                                    <span>
                                        <input class="input-readonly" type="checkbox" name="row-id-table-IR-${id_table_IR}" id="row-id-table-IR-${id_table_IR}" style="width: 45px" onclick="selectRowTable(this);">
                                    </span>
                                </td>
                                <td>
                                    <span id="row-cod_sistema-${id_table_IR}" data-export="0">${cod_sistema}</span>
                                </td>
                                <td>
                                    <span id="row-contribuinte-${id_table_IR}" data-export="0">${contribuinte}</span>
                                </td>
                                <td>
                                    <span id="row-cpf_cnpj-${id_table_IR}" data-export="0">${cpf_cnpj}</span>
                                </td>
                                <td>
                                    <span id="row-celular-${id_table_IR}" data-export="0">${celular}</span>
                                </td>
                                <td>
                                    <span id="row-telefone-${id_table_IR}" data-export="0">${telefone}</span>
                                </td>
                                <td>
                                    <span id="row-ano-${id_table_IR}" data-export="0">${ano}</span>
                                </td>
    
                                <td>
                                    <span id="row-status_smart_IR-${id_table_IR}" data-export="0">${status_smart_IR}</span>
                                    </td>
        
                                <td>
                                    <span id="row-dificuldade-${id_table_IR}" data-export="0">${dificuldade}</span>
                                </td>
                                <td>
                                    <span>
                                        <span>R$ </span>
                                        <input type="text" id="row-valor_ano_anterior-${id_table_IR}" value="${valor_ano_anterior}" data-export="0" maxlength="25" data-field-name="valor_ano_anterior" oninput="post_edit_value_IR(this);">
                                    </span>
                                </td>
                                <td>
                                    <span>
                                        <span>R$ </span>
                                        <input type="text" id="row-valor_ano_atual-${id_table_IR}" id="row-valor_ano_atual-${id_table_IR}" value="${valor_ano_atual}" data-export="0" maxlength="25" data-field-name="valor_ano_atual"  oninput="post_edit_value_IR(this);">
                                    </span>
                                </td>
                                <td>
                                    <span id="row-tt_comments-${id_table_IR}" data-export="0">${tt_comments}</span>
                                </td>
    
                                <td>
                                    <span id="row-status_pagamento_IR-${id_table_IR}" data-export="0">${status_pagamento_IR}</span>
                                </td>
                                
                                <td>
                                    <span id="row-info_forma_pagamento-${id_table_IR}" data-export="0">${info_forma_pagamento}</span>
                                </td>
    
                                <td>
                                    <span id="row-dt_pagamento_IR-${id_table_IR}" data-export="0">${dt_pagamento_IR}</span>
                                </td>
        
                                <td class="option-sticky-right">
                                    <span class="block-actions-icons">
                                        <i class="fa-solid fa-circle-info"  data-row-comment="${id_table_IR}" onclick="openModal_InfoIR(this);" title="informações"></i>
                                        <i class="fa-solid fa-trash-can"

                                            data-row-delete="${id_table_IR}"
                                            data-row-contribuinte="${contribuinte}"
                                            data-row-ano="${ano}"
                                            data-row-status_smart_IR="${status_smart_IR}"

                                            data-modal-name="confitm-delete-IR" onclick="displayModalDeleteIR(this);"></i>
                                    </span>
                                </td>
        
                            </tr>
                        `);
                        cont_row +=1;
                    }
                }
                    
            } else {
                break;
            }
        }
        // <i class="fa-solid fa-trash-can" data-row-delete="${id_table_IR}" data-modal-name="confitm-delete-IR" onclick="displayModalDeleteIR(this);"></i>
        table.querySelector("tbody").innerHTML = arr_elements_tr.join("");

        update_values_otions(data);
        

        return resolve();
    })
    // .then(()=>{
    //     renderizerTableAllDeliveriesIR();
    // });

}

async function check_filters_local_storage(filter_name, array_data_filter){
    try {
        let filter = await JSON.parse(window.localStorage.getItem(filter_name))["filter"];
        filter.includes("*")
        return filter;
    } catch (error) {
        window.localStorage.setItem(filter_name, JSON.stringify({"filter": array_data_filter}) );
        return null;
    }
}

async function update_filters_deliveries_IR(data=null){

    // console.log(" ------------- data_filters_deliveries_IR ------------- ")
    // console.log(data_filters_deliveries_IR)

    let filter_status_smart_IR =  document.getElementById("filter-status-smart-IR");
    let filter_status_pagamento = document.getElementById("filter-status-pagamento");


    let arr_elements_status_smart_IR = new Array();
    let arr_elements_status_pagamento = new Array();
    let value_aux = null;
    let value_check_aux = null;

    let arr_apply_filters = {
        "status_smart_IR": [],
        "status_pagamento": [],
    }

    
    if(data != null){
        data = data_filters_deliveries_IR;
    }
    for (let filter in arr_apply_filters){

        let filter_localStorage = await check_filters_local_storage(filter, data[filter]);

        // console.log(" ----------------- filter_localStorage ----------------- ")
        // console.log(filter_localStorage)

        // --------------------------------------------------------------------------------------------------------------- filter-status-smart-IR
        for (let i in data[filter]) {
            value_aux = await data[filter][i];
            value_check_aux = "";
            
            if (filter_localStorage != null){
                indexValueArr = filter_localStorage.includes("Todos");
                if (filter_localStorage == null || filter_localStorage.length == 0) { //  || value_aux == "Todos"
                    value_check_aux = "checked";
                }
                else if (filter_localStorage != null && filter_localStorage.includes(value_aux)){
                    value_check_aux = "checked";
                }
            }
            arr_apply_filters[filter].push(`
                <span>
                    <input type="checkbox" name="${value_aux}" id="${filter}_${value_aux}" ${value_check_aux} data-filter-name="${filter}"  data-value="${value_aux}"onclick="update_filter_localStorage(this);">
                    <label for="${value_aux}" data-filter-name="${filter}">${value_aux}</label>
                </span>
            `);
        }
    }
    

    filter_status_smart_IR.innerHTML = arr_apply_filters["status_smart_IR"].join("");
    filter_status_pagamento.innerHTML = arr_apply_filters["status_pagamento"].join("");

}

async function update_filter_localStorage(element){

    let filter_name = element.getAttribute("data-filter-name");
    let value = element.getAttribute("data-value");
    let filter_localStorage = JSON.parse(window.localStorage.getItem(filter_name))["filter"];
    // console.log(element)
    // console.log(filter_localStorage)
    let status_check = false;
    if(value == "Todos"){
        if (element.checked == true){
            filter_localStorage = data_filters_deliveries_IR[filter_name];
            status_check = true;
        } else {
            filter_localStorage = [];
        }
        document.querySelectorAll(`[data-filter-name="${filter_name}"]`).forEach((e)=>{
            e.checked = status_check;
        });
        window.localStorage.setItem( filter_name, JSON.stringify({"filter": filter_localStorage}) );
    }
    else {
        if (element.checked == true){
            filter_localStorage.push(value);
        }
        else {
            let indexArr = filter_localStorage.indexOf(value);
            if ( indexArr > -1){
                filter_localStorage.splice(indexArr, 1);
            }
        }
        window.localStorage.setItem( filter_name, JSON.stringify({"filter": filter_localStorage}) );
    }

    update_table_IR();
}

async function download_IR_CSV(){
    
    let csv_content = [];
    let arr_aux = [];
    document.querySelectorAll(`[data-table-header="table-IR"]`).forEach((header)=>{
        arr_aux.push(header.textContent.trim());

    })
    csv_content.push(arr_aux.join(";"));

    document.querySelectorAll(`[data-row-table-ir]`).forEach((row)=>{
        arr_aux = [];
        row.querySelectorAll(`td [data-export="0"]`).forEach((content)=>{
            let value = content.value || content.textContent;
            arr_aux.push(value.trim());
        });
        csv_content.push(arr_aux.join(";"));

    });
    csv_content = csv_content.join("\n");
    console.log(csv_content)

    const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), csv_content], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'Imposto de Renda.csv';
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}




