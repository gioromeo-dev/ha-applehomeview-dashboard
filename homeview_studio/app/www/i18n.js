// English translation layer for the (Italian-authored) editor.
// After each render, text nodes and placeholder/title attributes are mapped Italian -> English.
'use strict';
const I18N_EN = {
  // header / status / stage
  'Caricamento…': 'Loading…', 'Pronto': 'Ready', 'Errore': 'Error', 'Apri dashboard': 'Open dashboard',
  'Applica alla dashboard': 'Apply to dashboard', 'Applico…': 'Applying…', 'Annulla (Cmd/Ctrl+Z)': 'Undo (Cmd/Ctrl+Z)',
  'Modifiche non ancora applicate': 'Changes not applied yet', 'Dashboard aggiornata': 'Dashboard up to date',
  'Trascina gli elementi sulla griglia · trascina un quadrato per spostarlo (sopra un altro per scambiarli) · clic per modificarlo':
    'Drag items onto the grid · drag a tile to move it (onto another to swap them) · click to edit it',
  'Elementi': 'Items', 'Aspetto': 'Appearance', 'Comportamento': 'Behavior', 'Generale': 'General',
  // items tab
  'Widget': 'Widgets', 'Meteo': 'Weather', 'Orologio': 'Clock', 'Telecamera': 'Camera', 'Gruppo': 'Group',
  'Barra "Prossimi" in fondo': '"Up next" bar at the bottom', 'Mostra gli eventi dei calendari scelti in Generale': 'Shows events from the calendars chosen in General',
  'Dispositivi ed entità': 'Devices and entities', 'Cerca per nome, stanza o ID…': 'Search by name, room or ID…',
  'Tutti': 'All', 'Luci': 'Lights', 'Prese/Interruttori': 'Plugs/Switches', 'Scene': 'Scenes', 'Script': 'Scripts', 'Clima': 'Climate',
  'Media': 'Media', 'Sensori': 'Sensors', 'Sensori binari': 'Binary sensors', 'Telecamere': 'Cameras', 'Tapparelle': 'Covers',
  'Serrature': 'Locks', 'Ventole': 'Fans', 'Interruttori virtuali': 'Virtual switches', 'Automazioni': 'Automations', 'Altro': 'Other',
  'Tutte le stanze': 'All rooms', 'Mostra entità nascoste/di sistema': 'Show hidden/system entities',
  '…affina la ricerca per vedere le altre': '…refine the search to see the rest', 'Aggiungi': 'Add', 'Il': 'The',
  'aggiunge al gruppo': 'adds to the group',
  // inspector
  'Seleziona un quadrato nella griglia per modificarlo.': 'Select a tile in the grid to edit it.', 'Suggerimenti': 'Tips',
  "• Trascina un'entità dalla colonna di sinistra su una casella vuota, o premi": '• Drag an entity from the left column onto an empty cell, or press',
  '• Trascina un quadrato su un altro della stessa misura per scambiarli.': '• Drag a tile onto another one of the same size to swap them.',
  'Canc': 'Delete', 'elimina il quadrato selezionato,': 'removes the selected tile,', 'annulla.': 'undoes.',
  '• Le modifiche vengono salvate qui subito; premi': '• Changes are saved here right away; press',
  "per pubblicarle sull'iPad.": 'to publish them to the iPad.',
  'Dispositivo': 'Device', 'Entità': 'Entity', 'Nome (testo grande)': 'Name (large text)', 'Etichetta (testo piccolo)': 'Label (small text)',
  'vuota = stato automatico': 'empty = automatic state', 'Icona': 'Icon', 'sfoglia': 'browse', 'Stile del quadrato': 'Tile style',
  'Azione al tocco': 'Tap action', 'Destinazione': 'Destination', 'Dimensione (colonne × righe)': 'Size (columns × rows)',
  'Posizione': 'Position', 'Duplica': 'Duplicate', 'Elimina': 'Delete', 'Rimuovi': 'Remove', 'Su': 'Up', 'Giù': 'Down',
  'Nome': 'Name', 'Etichetta': 'Label', 'vuota = «2 accesi su 5»': 'empty = «2 on of 5»',
  'Pressione prolungata sul quadrato': 'Long press on the tile', 'Accendi / spegni tutto': 'Turn everything on / off', 'Nessuna': 'None',
  'Nessun dispositivo. Aggiungili qui sotto, con il': 'No devices yet. Add them below, with the',
  'nella lista a sinistra, o trascinandoli sul quadrato.': 'in the list on the left, or by dragging them onto the tile.',
  'Aggiungi un dispositivo': 'Add a device', 'Scegli…': 'Choose…', 'Aggiungi in blocco': 'Add in bulk', 'Aggiungi tutti': 'Add all',
  'Svuota gruppo': 'Empty group', "Sull'iPad:": 'On the iPad:', 'tocco': 'tap',
  '= apre il popup con tutti i dispositivi e i pulsanti «Accendi/Spegni tutto»;': '= opens the popup with every device and the «Turn all on/off» buttons;',
  'pressione prolungata': 'long press', '= accende o spegne tutto il gruppo.': '= turns the whole group on or off.',
  'non trovata': 'not found', 'Entità non trovata': 'Entity not found', 'Sicuro? Clicca di nuovo': 'Sure? Click again',
  // styles / taps / clocks
  'Automatico': 'Automatic', 'Pulsante vetro': 'Glass button', 'Ventola (icona che gira)': 'Fan (spinning icon)', 'Porta / finestra': 'Door / window',
  'Media player': 'Media player', 'Valore sensore': 'Sensor value', 'Tapparella': 'Cover', 'Serratura': 'Lock', 'Stato generico': 'Generic state',
  'Automatica': 'Automatic', 'Accendi / spegni': 'Toggle on / off', 'Apri dettagli': 'Open details', 'Vai a…': 'Go to…',
  'Originale': 'Original', 'Classico': 'Classic', 'Minimal': 'Minimal', 'Numeri grandi': 'Big numerals', 'Digitale': 'Digital',
  'Ore e minuti': 'Hours & minutes', 'Solare': 'Solar',
  // appearance
  'Temi rapidi': 'Quick themes', 'Vetro': 'Glass', 'Notte': 'Night', 'Pastello': 'Pastel', 'Sfondo': 'Wallpaper', 'Giorno': 'Day',
  'Sfondo principale (bordo blu).': 'Main wallpaper (blue border).',
  'Sfondo dopo il tramonto (bordo viola). Vuoto = sempre quello del giorno.': 'Wallpaper after sunset (purple border). Empty = always the day one.',
  'Scegliendo uno sfondo chiaro che ha una versione scura (-light/-dark) la imposto da sola per la notte.': 'Picking a light wallpaper that has a dark version (-light/-dark) sets it for the night automatically.',
  'Sfondo principale (bordo blu). Scegliendo uno sfondo chiaro che ha una versione scura (-light/-dark) la imposto da sola per la notte.':
    'Main wallpaper (blue border). Picking a light wallpaper that has a dark version (-light/-dark) sets it for the night automatically.',
  'Sfondo dopo il tramonto (bordo viola). Vuoto = sempre quello del giorno. Scegliendo uno sfondo chiaro che ha una versione scura (-light/-dark) la imposto da sola per la notte.':
    'Wallpaper after sunset (purple border). Empty = always the day one. Picking a light wallpaper that has a dark version (-light/-dark) sets it for the night automatically.',
  'Rimuovi notte': 'Remove night', 'I tuoi sfondi': 'Your wallpapers', 'Carica': 'Upload', 'scuro': 'dark', 'chiaro': 'light',
  'Oppure indirizzo immagine (giorno)': 'Or image address (day)', 'Luminosità sfondo': 'Wallpaper brightness', 'Quadrati': 'Tiles',
  'Opacità vetro (spento)': 'Glass opacity (off)', 'Colore quando acceso': 'Color when on', 'Intensità colore acceso': 'On color intensity',
  'Testo e icone (spento)': 'Text and icons (off)', 'Testo e icone (acceso)': 'Text and icons (on)', 'Sfocatura vetro': 'Glass blur',
  'Arrotondamento angoli': 'Corner radius', 'Ombra e riflessi': 'Shadow and highlights', 'Effetto vetro in rilievo': 'Raised glass effect',
  'Testi': 'Text', 'Dimensione nome': 'Name size', 'Dimensione etichetta': 'Label size', 'Dimensione icona': 'Icon size', 'Griglia': 'Grid',
  'Colonne': 'Columns', 'Spazio tra i quadrati': 'Space between tiles', 'Larghezza massima': 'Maximum width', 'Orologi': 'Clocks',
  'Quadrato orologio nella Home': 'Clock tile on Home', 'Orologio nella pagina Widget': 'Clock on the Widgets page',
  'Salvaschermo (a tutto schermo)': 'Screensaver (full screen)', 'Colore di sfondo del salvaschermo': 'Screensaver background color',
  'Colore numeri del salvaschermo': 'Screensaver numerals color',
  // behavior
  'Salvaschermo': 'Screensaver', 'Salvaschermo con orologio': 'Clock screensaver', 'Dopo un periodo di inattività (WallPanel)': 'After a period of inactivity (WallPanel)',
  'Attiva dopo (secondi)': 'Start after (seconds)', 'Schermo': 'Screen', 'Schermo intero': 'Full screen', 'Al primo tocco': 'On first touch',
  'Nascondi barra in alto': 'Hide top bar', 'Nascondi barra laterale': 'Hide sidebar', 'Modalità kiosk sempre attiva': 'Kiosk mode always on',
  "Per uscire: aggiungi ?disable_km all'indirizzo. Se spenta: tieni premuto l'orologio": 'To leave it: add ?disable_km to the address. When off: long-press the clock',
  'Navigazione': 'Navigation', 'Scorrimento col mouse': 'Mouse swiping', 'Clic e trascina per cambiare pagina su Mac/PC': 'Click and drag to change page on Mac/PC',
  'Animazione cambio pagina': 'Page change animation', 'Scorrimento': 'Slide', 'Dissolvenza': 'Fade', 'Rotazione': 'Flip',
  'Scorrimento circolare': 'Wrap around', "Dall'ultima pagina torna alla prima": 'From the last page back to the first', 'Pagina Widget': 'Widgets page',
  'Pagina Telecamere': 'Cameras page', 'Pressione prolungata su un quadrato': 'Long press on a tile', 'Vibrazione al tocco': 'Haptic feedback',
  "Solo nell'app Home Assistant": 'Home Assistant app only',
  // screensaver faces
  'Quadranti del salvaschermo': 'Screensaver faces', 'Scegli quali quadranti mostrare e in che ordine: si alternano da soli.': 'Choose which faces to show and in what order: they rotate automatically.',
  'Foto': 'Photos', 'Flusso': 'Flow', 'Meridiana': 'Meridian', 'Calendario': 'Calendar',
  "L'orologio scelto in Aspetto, a tutto schermo": 'The clock chosen in Appearance, full screen', 'Cornice digitale con le tue foto o i tuoi sfondi': 'Digital frame with your photos or wallpapers',
  'Colori in movimento, più vivi quando rileva movimento': 'Moving colors, brighter when motion is detected', "Numeri che si accendono e sfumano seguendo l'ora": 'Numerals that light up and fade with the time',
  'Temperatura, condizioni e prossimi giorni': 'Temperature, conditions and the next days', 'Data e prossimi impegni': 'Date and upcoming events',
  'Cambia quadrante ogni (secondi)': 'Change face every (seconds)', 'Foto dalla cartella Photo Slideshow': 'Photos from the Photo Slideshow folder',
  'Media → Media locali → Photo Slideshow. Se è vuota uso i tuoi sfondi': 'Media → Local media → Photo Slideshow. If empty, your wallpapers are used',
  'Cambia foto ogni (secondi)': 'Change photo every (seconds)', 'Sensore di movimento per il quadrante Flusso': 'Motion sensor for the Flow face',
  'Modalità notte': 'Night mode', 'Salvaschermo più scuro e caldo di notte': 'Darker, warmer screensaver at night', 'Dalle': 'From', 'Alle': 'To', 'Luminosità di notte': 'Night brightness',
  // cameras tab
  'Disposizione': 'Layout', 'Automatica (1 = schermo intero, 2–4 = 2 colonne, 5+ = 3 colonne)': 'Automatic (1 = full screen, 2–4 = 2 columns, 5+ = 3 columns)',
  'Griglia con colonne a scelta': 'Grid with chosen columns', 'Una grande + le altre di lato': 'One large + the others on the side',
  "Spunta quelle da mostrare, ordinale con le frecce (la prima è quella grande), rinominale e scegli come adattare l'immagine.": 'Tick the ones to show, order them with the arrows (the first is the large one), rename them and choose how the image fits.',
  'Riempi': 'Fill', 'Intera': 'Fit', 'Opzioni': 'Options', 'Mostra i nomi': 'Show names', 'Al tocco': 'On tap',
  'Apri a schermo intero (diretta)': 'Open full screen (live)', 'Aggiorna le immagini ogni': 'Refresh images every',
  'Spazio tra le telecamere': 'Space between cameras', 'Nessuna telecamera selezionata': 'No camera selected',
  // proposal
  'Riorganizza in un attimo': 'Reorganize in a moment',
  'Analizzo tutti i tuoi dispositivi e propongo una Home: gruppi per luci, prese, scene e temperature, più clima, porte, media e telecamera.': 'Analyzes all your devices and proposes a Home: groups for lights, plugs, scenes and temperatures, plus climate, doors, media and camera.',
  'Proponi una Home': 'Propose a Home', 'Porta': 'Door', 'Finestra': 'Window', 'Prese': 'Plugs', 'Temperature': 'Temperatures', 'Interruttori': 'Switches',
  'Tieni': 'Keep', 'Torna a prima': 'Go back', 'Proposta:': 'Proposal:',
  'quadrati. Puoi ancora modificarli; premi': 'tiles. You can still edit them; press', 'per pubblicarla.': 'to publish it.',
  // icon picker
  'Scegli': 'Choose', "Usa l'icona del dispositivo": "Use the device's icon", 'Icona automatica': 'Automatic icon', 'Suggerite': 'Suggested',
  'Cerca tra tutte le icone (nomi in inglese, es. sofa)…': 'Search all icons (e.g. sofa)…', 'Nessuna icona trovata': 'No icons found',
  'Icone delle schede (vuota = mostra il nome)': 'Tab icons (empty = show the name)', 'Home': 'Home',
  // general
  'Dashboard': 'Dashboard', 'Titolo': 'Title', 'Indirizzo (deve contenere un trattino)': 'Address (must contain a hyphen)', 'Sorgenti': 'Sources',
  'Telecamera principale (pagina Telecamere e campanello)': 'Main camera (Cameras page and doorbell)',
  'Evento campanello (apre la telecamera quando suonano)': 'Doorbell event (opens the camera when someone rings)', 'Nessuno': 'None',
  'Calendari': 'Calendars', 'Nessun calendario trovato': 'No calendars found',
  'Scegli quali telecamere mostrare e in che ordine (1 = schermo intero, 2–4 = griglia 2×2, 5+ = griglia 3 colonne).': 'Choose which cameras to show and in what order (1 = full screen, 2–4 = 2×2 grid, 5+ = 3-column grid).',
  'Nessuna telecamera trovata': 'No cameras found', 'Ripristino': 'Restore',
  'Prima di ogni "Applica" salvo una copia della dashboard. Puoi tornare a una versione precedente.': 'Before every "Apply" a copy of the dashboard is saved. You can go back to a previous version.',
  'Ripristina': 'Restore', 'Nessuna copia ancora': 'No copies yet', 'Riporta layout iniziale': 'Reset to the initial layout',
  'Lingua': 'Language', 'Automatica (come Home Assistant)': 'Automatic (same as Home Assistant)',
  // preview tiles and states
  'Casa': 'Home', 'Prossimi': 'Up next', 'nessun calendario': 'no calendar', 'Vuoto': 'Empty', 'Spento': 'Off', 'Tutto spento': 'All off',
  'Tutti accesi': 'All on', 'Scena': 'Scene', 'Live': 'Live', 'Aperta': 'Open', 'Chiusa': 'Closed', 'Aperto': 'Open', 'Chiuso': 'Closed',
  'Acceso': 'On', 'Inattivo': 'Idle', 'In pausa': 'Paused', 'In riproduzione': 'Playing', 'Non risponde': 'Not responding', 'Bloccata': 'Jammed',
  'A casa': 'Home', 'Fuori': 'Away', 'Sereno': 'Clear', 'Nuvoloso': 'Cloudy', 'Allerta': 'Warning', 'Nebbia': 'Fog', 'Grandine': 'Hail',
  'Temporale': 'Thunderstorm', 'Poco nuvoloso': 'Partly cloudy', 'Pioggia forte': 'Pouring', 'Pioggia': 'Rain', 'Neve': 'Snow',
  'Nevischio': 'Sleet', 'Soleggiato': 'Sunny', 'Ventoso': 'Windy', 'In apertura': 'Opening', 'In chiusura': 'Closing',
  // toasts
  'Modifica annullata': 'Change undone', 'Già presenti nel gruppo': 'Already in the group', 'Sfondo caricato': 'Wallpaper uploaded',
  'Di notte userò la versione scura': 'The dark version will be used at night', 'Dashboard ripristinata': 'Dashboard restored',
  'Layout iniziale ripristinato (non ancora applicato)': 'Initial layout restored (not applied yet)',
  "Non c'è spazio lì: libera le caselle o scegli un'altra posizione": 'No room there: free up the cells or pick another position',
  'Quella casella è occupata: trascina su una casella vuota (o sopra un gruppo per aggiungerla)': 'That cell is taken: drop onto an empty cell (or onto a group to add it)',
  'Dimensioni diverse: non posso scambiarli qui': "Different sizes: they can't be swapped here",
  "Non c'è spazio per questa dimensione lì": 'No room for this size there', "Non c'è spazio: sposta prima i quadrati vicini": 'No room: move the nearby tiles first',
  'Casella occupata o fuori griglia': 'Cell taken or outside the grid', 
  "aggiornata. Ricarica la pagina sull'iPad.": 'updated. Reload the page on the iPad.',
};
const I18N_PATTERNS = [
  [/^(\d+) entità · (\d+) già sulla dashboard$/, '$1 entities · $2 already on the dashboard'],
  [/^Crea un gruppo con queste (\d+) entità$/, 'Create a group with these $1 entities'],
  [/^Aggiungi tutte \((\d+)\)$/, 'Add all ($1)'],
  [/^Dispositivi nel gruppo \((\d+)\)$/, 'Devices in the group ($1)'],
  [/^colonna (\d+), riga (\d+)$/, 'column $1, row $2'],
  [/^(\d+) access?[oi] su (\d+)$/, '$1 on of $2'],
  [/^Notte: (.+)$/, 'Night: $1'],
  [/^(mdi:[a-z0-9-]+) \(dispositivo\)$/, '$1 (device)'],
  [/^Carico (.+)…$/, 'Uploading $1…'],
  [/^Automatico \((.+)\)$/, (m, a) => 'Automatic (' + (I18N_EN[a] || a) + ')'],
  [/^(Dispositivo|Gruppo|Meteo|Orologio|Telecamera)( · .*)?$/, (m, k, rest) => (I18N_EN[k] || k) + (rest || '').replace(' · stato: ', ' · state: ')],
  [/^(.+) · (Raffredda|Riscalda|Deumidifica|Ventola|Auto)$/, (m, a, b) => a + ' · ' + ({Raffredda: 'Cooling', Riscalda: 'Heating', Deumidifica: 'Drying', Ventola: 'Fan', Auto: 'Auto'})[b]],
  [/^Aperta · (\d+)%$/, 'Open · $1%'],
  [/^(.+) aggiunto a «(.+)»$/, '$1 added to «$2»'], [/^(\d+) dispositivi aggiunti a «(.+)»$/, '$1 devices added to «$2»'],
  [/^(\d+) elementi sono fuori dalla griglia \(colonne ridotte\): aumenta le colonne o spostali$/, '$1 items are outside the grid (fewer columns): add columns or move them'],
  
  [/^(Errore|Salvataggio fallito|Caricamento fallito|Download fallito|Impossibile caricare i dati): (.*)$/,
    (m, a, b) => ({'Errore': 'Error', 'Salvataggio fallito': 'Saving failed', 'Caricamento fallito': 'Upload failed', 'Download fallito': 'Download failed', 'Impossibile caricare i dati': 'Could not load data'})[a] + ': ' + b],
  [/^Il percorso della dashboard deve contenere un trattino, es\. home-view$/, 'The dashboard address must contain a hyphen, e.g. home-view'],
];
let UI_LANG = 'it';
function trText(s) {
  if (UI_LANG !== 'en') return s;
  const m = s.match(/^(\s*)([\s\S]*?)(\s*)$/); const core = m[2];
  if (!core) return s;
  if (Object.prototype.hasOwnProperty.call(I18N_EN, core)) return m[1] + I18N_EN[core] + m[3];
  for (const [re, rep] of I18N_PATTERNS) if (re.test(core)) return m[1] + core.replace(re, rep) + m[3];
  return s;
}
function tr(s) { return trText(s); }
function translateDOM(root) {
  if (!root) return;
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    if (n.parentNode && /^(SCRIPT|STYLE)$/.test(n.parentNode.nodeName)) continue;
    if (n.parentElement && n.parentElement.closest('[data-raw]')) continue;
    if (n.__it === undefined) n.__it = n.nodeValue;
    const v = UI_LANG === 'en' ? trText(n.__it) : n.__it;
    if (n.nodeValue !== v) n.nodeValue = v;
  }
  (root.querySelectorAll ? root.querySelectorAll('[placeholder],[title]') : []).forEach(el => {
    for (const a of ['placeholder', 'title']) {
      if (!el.hasAttribute(a)) continue;
      const key = '__it_' + a;
      if (el[key] === undefined) el[key] = el.getAttribute(a);
      el.setAttribute(a, UI_LANG === 'en' ? trText(el[key]) : el[key]);
    }
  });
}
