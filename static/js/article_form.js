function addIngredientsForm() {
    let div = document.getElementById("ingredients");
    let form = document.getElementById("ingredient_form");
    let newForm = form.cloneNode(true);
    newForm.setAttribute("class", "ingredient_form");
    div.appendChild(newForm);
    // Работает только с div-ами
}