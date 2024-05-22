var data_table_deliveries_IR = null;
var data_filters_deliveries_IR = null;
var data_table_clients = null;
var arr_events_stOut = new Array();
var data_all_clients_IR;    // utilizado para base de clientes de imposto de renda.
var data_pend_IR;
var data_all_companies;     // utilizado para base de empresas do acessórias.
var data_table_import_txt_to_JB;

async function get_info_session_company(){
    try {
        let company_session_info;
        company_session_info = JSON.parse(window.localStorage.getItem("session_company_info"));
        if(company_session_info["company_session"]["session_company_code"]){
            return company_session_info;
        }
        return null;
    } catch (error) {
        return null;
    }
}

async function sortDataObject(objeto) {
    // Convertendo o objeto em um array de pares [chave, valor]
    
    const sortData = [];
    for (let i in objeto){
        sortData.push({
            "razao_social": objeto[i]["razao_social"],
            "id_acessorias": objeto[i]["id_acessorias"],
            "cnpj": objeto[i]["cnpj"],
            "JB_CODE": objeto[i]["JB_CODE"],
        })
    }

    // Ordenando o array de pares com base na "razao_social"
    sortData.sort((a, b) => {
        const razaoSocialA = a["razao_social"];
        const razaoSocialB = b["razao_social"];
        return razaoSocialA.localeCompare(razaoSocialB);
    });

    return sortData;
}

async function get_all_companies(url){
    let body = {
        "query_version": "1",
        "cols_names": ["*"],
        "order_by": ["razao_social"],
    }
    fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json", "redirect": "follow"},
        body: JSON.stringify(body)
    })
    .then((data)=>{
        return data.json();
    })
    .then((data)=>{
        data_all_companies = JSON.parse(data["data"]);
        update_dropdown_all_companies_session(data);
        updateDropdownAllCompaniesCreateNewApontHours(data_all_companies);
        
        return;
    })
    .then(()=>{
        updateDropdowCompanySessionActive();
    });  
    
}

async function updateDropdowCompanySessionActive(){

    let row_company = null;
    try {

        let company_session = JSON.parse(window.localStorage.getItem("session_company_info"))["company_session"];
        let session_company_code    = company_session["session_company_code"];
        let session_company_code_JB = company_session["session_company_code_JB"];
        let session_company_name    = company_session["session_company_name"];
        let rows = document.querySelectorAll(`[data-row-company`);
        document.querySelector(`[data-row-company="row_${session_company_code}"`).classList.remove("active");
        rows.forEach((e)=>{
            row_company = `row_${session_company_code}`;
            if(e.getAttribute("data-row-company") == row_company){
                e.classList.add("active");
                e.querySelectorAll("div")[0].querySelector("input").checked = true;
                document.getElementById("company_session_name").value = `[${session_company_code} / ${session_company_code_JB}] - ${session_company_name}`;
                document.getElementById("company_session_code").value = session_company_code;
            } else {
                e.classList.remove("active");
                e.querySelectorAll("div")[0].querySelector("input").checked = false;
            }
        });

    } catch (error) {};
}

function testValueCompanyCodeJB(value){
    const regex = /^\d+$/;
    return regex.test(value);
}

async function update_dropdown_all_companies_session(data){
    data = await sortDataObject(data_all_companies);
    console.log(data)
    try {
        let id_acessorias, cnpj, razao_social;
        let elem_new_ul = [];
        let block_dropdown = document.querySelector(".block-dropdown-all-companies").querySelector("ul");
        for(let i in data){
            id_acessorias   = data[i]["id_acessorias"];
            cnpj            = data[i]["cnpj"];
            razao_social    = data[i]["razao_social"];
            jb_code         = data[i]["JB_CODE"];
            elem_new_ul.push(`
                <li data-row-company="row_${data[i]["id_acessorias"]}">
                    <div>
                        <input type="checkbox" name="row_${data[i]["id_acessorias"]}" id="row_${data[i]["id_acessorias"]}" onclick="selectCompany(this);" >
                    </div>

                    <div class="block-info-id-acessorias" data-code-generic="row_code_company_${data[i]["id_acessorias"]}">
                        <span>${id_acessorias}</span>
                    </div>
                    <div data-info-company="row_${data[i]["id_acessorias"]}">
                        <span>${cnpj}</span>
                        <span>${razao_social}</span>
                    </div>
                    
                    <div data-info-code-company="row_${data[i]["id_acessorias"]}">
                        <span>${jb_code}</span>
                        <i class="fa-regular fa-pen-to-square" data-btn-edit-code-company="${data[i]["id_acessorias"]}" onclick="editCompanyCodeJB(this);"></i>
                    </div>
                </li>
            `);
        }
        block_dropdown.innerHTML = elem_new_ul.join("");
    } catch (error) {};
}

async function editCompanyCodeJB(element){
    let id_row = element.getAttribute("data-btn-edit-code-company");
    console.log(`>>> id_row: ${id_row}`)
    let id_acessorias   = document.querySelector(`[data-code-generic="row_code_company_${id_row}"]`).querySelectorAll("span")[0].textContent;
    let cnpj            = document.querySelector(`[data-info-company="row_${id_row}"]`).querySelectorAll("span")[0].textContent;
    let razao_social    = document.querySelector(`[data-info-company="row_${id_row}"]`).querySelectorAll("span")[1].textContent;
    let company_code_JB = document.querySelector(`[data-info-code-company="row_${id_row}"]`).querySelectorAll("span")[0].textContent;
    let testValue = testValueCompanyCodeJB(company_code_JB);
    if(!testValue){
        company_code_JB = "";
    }
    document.querySelector(`[data-info-company-session="id_acessorias"]`).textContent   = id_acessorias;
    document.querySelector(`[data-info-company-session="cnpj"]`).textContent            = cnpj;
    document.querySelector(`[data-info-company-session="razao_social"]`).textContent    = razao_social;
    document.getElementById(`company_code_JB`).value                                    = company_code_JB;




    document.querySelector(".container-config-account-code-JB").classList.add("active");
}

async function filterCompanySession(text=null){
    let rows, id_acessorias, cnpj, razao_social, company_code_JB;
    let input_company_session = document.getElementById("company_session_name");
    if (text == null){
        text = input_company_session.value;
    }
    text = text.toUpperCase();

    if(text.split("] - ").length == 2){
        text = text.split("] - ")[1].trim();
        element.value = text.toUpperCase();
    } else {
        input_company_session.value = text;
    }

    rows = document.querySelectorAll(`[data-row-company]`).forEach((row)=> {

        id_acessorias = row.querySelector(`.block-info-id-acessorias`).querySelectorAll("span")[0].textContent.trim().toUpperCase();
        cnpj = row.querySelector(`[data-info-company]`).querySelectorAll("span")[0].textContent.trim().toUpperCase();
        razao_social = row.querySelector(`[data-info-company]`).querySelectorAll("span")[1].textContent.trim().toUpperCase();
        company_code_JB = row.querySelector(`[data-info-code-company]`).querySelectorAll("span")[0].textContent.trim().toUpperCase();
        
        
        if ( razao_social.indexOf(text) > -1 || cnpj.indexOf(text) > -1 || id_acessorias.indexOf(text) > -1 || company_code_JB.indexOf(text) > -1 ){
            row.style.display = "flex";
        }
        else {
            row.style.display = "none";
        }

    });


}

async function updateDropdownAllCompaniesCreateNewApontHours(data_companies){
    try {
        let arr_rows_dropdown = [];
        let dropdown = document.querySelector(".block-dropdown-all-companies-create-new-apont-hours").querySelector("ul");
        for(let i in data_companies){
            arr_rows_dropdown.push(`
                <li data-row-company-apont-hours="${data_companies[i].id_acessorias}" onclick="selectCompanyApontHour(this)" onclick="checkInputsFormCreateNewApontHours(this);">
                    <span>${data_companies[i].id_acessorias}</span>
                    <span>${data_companies[i].razao_social}</span>
                </li>
            `);
        }
        dropdown.innerHTML = arr_rows_dropdown.join("");
    } catch (error) {};
}

async function updateLink(){

    let block_name = await window.localStorage.getItem("select_link_activity");
    if(block_name == undefined ||block_name == null){
       block_name = "apont-hours";
        window.localStorage.setItem("select_link_activity", block_name);
    }
    document.querySelectorAll(`[data-link]`).forEach((e)=>{
        e.classList.remove("active");
    });

    try {
        // ---------------------------------------------------------------------------
        document.querySelector(`[data-link="${block_name}"]`).classList.add("active");
        document.querySelectorAll(`[data-block-name]`).forEach((e)=>{
            if(e.getAttribute("data-block-name") == block_name){
                e.classList.add("active");
            } else {
                e.classList.remove("active");
            }
        });
    } catch (error) {};
}

    