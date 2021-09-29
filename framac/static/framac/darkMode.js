var r = document.querySelector(':root');
var dark_mode = false;

function changeColors() {
  if (dark_mode === false) {
    r.style.setProperty('--main', '#7289da');

    r.style.setProperty('--button', '#2e3136');
    r.style.setProperty('--button-hover', '#282b30');
    r.style.setProperty('--button-border', '#09365f');
    r.style.setProperty('--even-button', '#9b7de0');
    r.style.setProperty('--odd-button', '#65bee2');

    r.style.setProperty('--text', 'white');
    r.style.setProperty('--right-bar', '#282b30');
    r.style.setProperty('--tab', '#282b30');
    r.style.setProperty('--tab-hover', '#25252f');

    r.style.setProperty('--current-page', '#43b581');
    r.style.setProperty('--current-hover', '#26634b');

    r.style.setProperty('--code-background', '#818386');
    r.style.setProperty('--code-text', 'white');
    dark_mode = true;
  }
  else {
    r.style.setProperty('--main', '#dac393');

    r.style.setProperty('--button', '#d44b27');
    r.style.setProperty('--button-hover', '#aead8a');
    r.style.setProperty('--button-border', '#e98f47');
    r.style.setProperty('--even-button', '#d7ebcc');
    r.style.setProperty('--odd-button', '#f5d4af');

    r.style.setProperty('--text', '#1f4228');
    r.style.setProperty('--right-bar', '#e98f47');
    r.style.setProperty('--tab', 'white');
    r.style.setProperty('--tab-hover', '#aead8a');

    r.style.setProperty('--current-page', '#4caf50');
    r.style.setProperty('--current-hover', '#68f370');

    r.style.setProperty('--code-background', 'white');
    r.style.setProperty('--code-text', 'black');
    dark_mode = false;
  }
}

