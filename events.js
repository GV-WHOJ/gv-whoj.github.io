/*
  EVENTS
  ------
  RA events shown in a banner at the top of the page on the day they happen.
  Add and edit these from the Admin page. You can also edit this file by hand.

  Each event:
    id      A unique id (the Admin page makes these for you)
    title   What residents see in bold
    about   One or two sentences about the event
    date    The day, written YYYY-MM-DD
    start   Start time in 24 hour time, like "20:00"
    end     Optional end time. With it, the banner says "Happening now" until it ends,
            then disappears. Without it, the banner stays up all day.
    where   Where it is

  Old events can stay here; they stop showing once the day is over.
*/

window.EVENTS = [
  {
    "id": "emwci38x2h239",
    "title": "This is a test",
    "about": "There are things happening, trust",
    "date": "2026-11-12",
    "start": "13:00",
    "where": "Hoobler 1st Floor Lobby",
    "end": "18:20"
  },
  {
    "id": "emwef4tyyomd8",
    "title": "HoobsGiving!",
    "about": "Come share or partake in a Thanksgiving feast -- Hoobler style!",
    "date": "2026-11-17",
    "start": "20:00",
    "where": "Hoobler 1st Floor Lobby",
    "end": "21:00"
  }
];
