button = document.getElementsByClassName("button")[0];
text = document.getElementsByClassName("text")[0];

function displayText() {
    text.innerHTML = "Me may dep:)"
}

button.addEventListener('click', displayText);