//dropdown
const droptekst = document.querySelector('.droptekst');
const dropdownIndhold = document.querySelector('.dropdown_indhold');
 
droptekst.addEventListener('click', () => {
    if (dropdownIndhold.classList.contains('aktiv')) {
        dropdownIndhold.classList.remove('aktiv');
    } 
    else {
        dropdownIndhold.classList.add('aktiv');
    }
});

document.addEventListener('click', (luk) => {
    if (!luk.target.closest('.dropdown')) {
        dropdownIndhold.classList.remove('aktiv');
    }
});

//nedtælling
const nedtælling = document.getElementById('nedtælling');

const dåbsdag = new Date('2026-09-05');
const idag = new Date();
const forskel = dåbsdag - idag;
const dage = Math.ceil(forskel / (1000 * 60 * 60 * 24));

nedtælling.textContent = 'Der er ' + dage + ' dage til dåben';

//tilmelding
const vælgNavn = document.getElementById('navn');
const vælgStatus = document.getElementById('status');
const gemSvar = document.getElementById('gem_svar');
const svaret = document.getElementById('svaret');

async function main() {
    const respons = await fetch('/gæster');
    const gæster = await respons.json();
    navne(gæster);
    renderListe(gæster);
}

function navne(gæster) {
    vælgNavn.innerHTML = '<option value="">Navn?</option>';
    gæster.forEach(gæst => {
        const navnValgt = document.createElement('option');
        navnValgt.value = gæst.navn;
        navnValgt.textContent = gæst.navn;
        vælgNavn.append(navnValgt);
    });
}

function renderListe(gæster) {
    const samletSvar = document.getElementById('gæsteliste');
    const kategorier = ['Deltager', 'Deltager kun ved dåb', 'Deltager ikke', 'Mangler svar'];
    samletSvar.innerHTML = '';

    kategorier.forEach(kategori => {
        const grupper = gæster.filter(gruppe => gruppe.status === kategori);
        const filtergruppe = document.createElement('div');

        if (kategori === 'Mangler svar') {
            filtergruppe.className = 'kategori mangler_svar';
        } 
        else {
            filtergruppe.className = 'kategori';
        }

        filtergruppe.innerHTML = '<h3>' + kategori + ' (' + grupper.length + ')</h3><ul>' + grupper.map(gruppe => '<li>' + gruppe.navn + '</li>').join('') + '</ul>';
        samletSvar.append(filtergruppe);
    })
}

gemSvar.addEventListener('click', async () => {
    const navn = vælgNavn.value;
    const status = vælgStatus.value;
 
    if (!navn) { svaret.textContent = 'Vælg venligst et navn.'; return; }
 
    const respons = await fetch('/gæster', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ navn, status })
    });
 
    const svar = await respons.json();
 
    const opdateret = await fetch('/gæster');
    const gæster = await opdateret.json();
    renderListe(gæster);
 
    vælgNavn.value = '';
    vælgStatus.value = 'Deltager';
    svaret.textContent = svar.besked;
});

main();
