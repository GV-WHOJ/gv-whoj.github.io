/*
  NOTICES
  -------
  Important policy changes shown in a banner above everything else, until a resident dismisses it.
  A dismissed notice stays hidden on that device. To bring it back for everyone, change its id.

  Each notice:
    id         A short unique name. Change it to show the notice again to people who dismissed it.
    from       First day to show it, written YYYY-MM-DD
    until      Last day to show it, written YYYY-MM-DD
    effective  The day the change starts. The tag says "Starts ..." before this day and "In effect now" after.
    title      The headline
    items      Up to three points. Each has an icon ("id", "lock", or "bell"), a short bold title, and one or two sentences.
    link       The "Read the full details" button: text, and where it goes (like "#overnight")

  Old notices can stay here; they stop showing after their last day.
*/

window.NOTICES = [
  {
    id: "overnight-access-2026-11",
    from: "2026-11-20",
    until: "2026-12-14",
    effective: "2026-11-30",
    title: "New overnight door access, every night from 10pm → 6am",
    items: [
      { icon: "id", title: "Enter through the main door", text: "Housing staff may ask to see your GV ID before you come in. Have it ready at the housing desk just inside the main doors." },
      { icon: "lock", title: "Side doors lock at 10pm", text: "Card readers on every other exterior door stop working. Those doors are for emergency exit only." },
      { icon: "bell", title: "An alarm will sound", text: "Pushing open a side door sets off an alarm right away. Leaving? Use the main door unless it is an emergency." }
    ],
    link: { text: "Read the full details", href: "#overnight" }
  }
];
