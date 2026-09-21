def checkbox_si_no(value: bool) -> str:
    return "☑ Sí  ☐ No" if value else "☐ Sí  ☑ No"


def checkbox_ok_fallo(ok: bool) -> str:
    return "☑ OK  ☐ Fallo" if ok else "☐ OK  ☑ Fallo"


def checkbox_ok_na(ok: bool) -> str:
    return "☑ OK  ☐ N/A" if ok else "☐ OK  ☑ N/A"
