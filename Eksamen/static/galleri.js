const uploadknap = document.getElementById('upload_knap');
const filinput = document.getElementById('fil_input');
const uploadbillede = document.getElementById('upload_billede');
const billedgalleri = document.getElementById('billede_galleri');

async function hentGalleri() {
    const billede_svar = await fetch('/galleri/filer');
    const filer = await billede_svar.json();

    billedgalleri.innerHTML = '';

    filer.forEach(fil => {
        if (fil.type === 'billede') {
            const img = document.createElement('img');
            img.src = fil.url;
            img.alt = 'Billede fra dåben';
            billedgalleri.append(img);
        }
        else {
            const video = document.createElement('video');
            video.src = fil.url;
            video.controls = true;
            billedgalleri.append(video);
        }
    });
}

uploadknap.addEventListener('click', async () => {
    const nyefiler = filinput.files;

    if (nyefiler.length === 0) {
        uploadbillede.textContent = 'Vælg mindst én fil.';
        return;
    }

    for (const fil of nyefiler) {
        const data = new FormData();
        data.append('fil', fil);

        const svar = await fetch('/galleri/upload', {
            method: 'POST',
            body: data
        }).then(retur => retur.json());
        uploadbillede.textContent = svar.besked;
    }

    filinput.value = '';
    hentGalleri();
});

hentGalleri();
