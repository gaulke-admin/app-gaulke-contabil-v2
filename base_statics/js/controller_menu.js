function setMenulink(element){

    let url = element.getAttribute("data-menu-url-link");
    let menu_link = element.getAttribute("data-menu-link");
    window.localStorage.setItem("menu_link", menu_link);
    updateLinkMenu();
    window.location.href = url;

}

function updateLinkMenu(){

    let menu_link = window.localStorage.getItem("menu_link");

    if (menu_link == null) {
        menu_link = document.querySelector(`[data-name-page]`).getAttribute("data-name-page");
        window.localStorage.setItem("menu_link", menu_link);
    }

    document.querySelectorAll("[data-menu-link]").forEach((e)=>{
        
        try {
            e.classList.remove("active");
            e.querySelector("i").classList.remove("active");
            e.querySelector("span").classList.remove("active");

            if(e.getAttribute("data-menu-link") == menu_link && e.getAttribute("data-menu-link") != "config_users"){
                    e.classList.add("active");
                    e.querySelector("i").classList.add("active");
                    e.querySelector("span").classList.add("active");
        
                    url = e.getAttribute("data-menu-url-link");
                }
            }
        catch (error) {};

    });
}

function displayDropdownMenuAsidebar(element){
    console.log(element)

    let menu_controller;
    let dropdown_index = element.getAttribute("data-dropdown-menu-asidebar-article");
    let ul = document.querySelector(`[data-dropdown-menu-asidebar-ul="${dropdown_index}"]`);
    ul.classList.toggle("active");

    try {
        menu_controller = JSON.parse(window.localStorage.getItem("status_menu_asidebar"))["status"];
        
    } catch (error) {
        window.localStorage.setItem("status_menu_asidebar", JSON.stringify({"status": {}}));
        menu_controller = JSON.parse(window.localStorage.getItem("status_menu_asidebar"))["status"];
    }

    if (ul.classList.contains("active")){
        menu_controller[dropdown_index] = "1";
    } else {
        menu_controller[dropdown_index] = "0";
    }
    window.localStorage.setItem("status_menu_asidebar", JSON.stringify({"status": menu_controller}));

}


function updateStatusDropdownMenuAsidebar () {
    try {
        menu_controller = JSON.parse(window.localStorage.getItem("status_menu_asidebar"))["status"];
        console.log(menu_controller)
        for (let key in menu_controller){
            if(menu_controller[key] == "1"){
                document.querySelector(`[data-dropdown-menu-asidebar-ul="${key}"]`).classList.add("active");
            } else {
                document.querySelector(`[data-dropdown-menu-asidebar-ul="${key}"]`).classList.remove("active");
            }
        }
        
    } catch (error) {
        window.localStorage.setItem("status_menu_asidebar", JSON.stringify({"status": {}}));
        menu_controller = JSON.parse(window.localStorage.getItem("status_menu_asidebar"))["status"];
    }
}