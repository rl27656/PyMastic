"""
Mechanistic-empirical transfer functions for flexible pavement design life.

Converts critical strains from a layered elastic analysis (e.g. PyMastic)
into allowable load repetitions to failure (Nf for fatigue cracking,
Nd for rutting).

References
----------
Asphalt Institute (1981, 1991), MS-1: Thickness Design Manual.
Huang, Y.H. (2004), Pavement Analysis and Design, 2nd ed., Ch. 3 & 11.
ARA, Inc. / NCHRP 1-37A (2004), Guide for Mechanistic-Empirical Design of
    New and Rehabilitated Pavement Structures, Part 3, Ch. 3
    (bottom-up fatigue cracking model).
"""


# ---------------------------------------------------------------------------
# Asphalt Institute (1981) models
# ---------------------------------------------------------------------------

def fatigue_life_ai(eps_t, E1_psi, f1=0.0796, f2=3.291, f3=0.854, shift_factor=1.0):
    """
    Asphalt Institute fatigue cracking model.

    Nf = f1 * eps_t^-f2 * E1^-f3

    Parameters
    ----------
    eps_t : float
        Tensile strain magnitude at the bottom of the AC layer (in/in).
    E1_psi : float
        AC layer modulus (psi).
    f1, f2, f3 : float
        Model coefficients. Defaults are the AI (1981) 50%-reliability values.
    shift_factor : float
        Optional lab-to-field shift factor (multiplies Nf). Default 1.0.

    Returns
    -------
    Nf : float
        Allowable number of load repetitions before fatigue cracking.
    """
    eps_t = abs(eps_t)
    return f1 * eps_t ** (-f2) * E1_psi ** (-f3) * shift_factor


def rutting_life_ai(eps_c, f4=1.365e-9, f5=4.477, shift_factor=1.0):
    """
    Asphalt Institute subgrade rutting (permanent deformation) model.

    Nd = f4 * eps_c^-f5

    Parameters
    ----------
    eps_c : float
        Compressive strain magnitude at the top of the subgrade (in/in).
    f4, f5 : float
        Model coefficients. Defaults are the AI (1981) 50%-reliability values.
    shift_factor : float
        Optional lab-to-field shift factor (multiplies Nd). Default 1.0.

    Returns
    -------
    Nd : float
        Allowable number of load repetitions before rutting failure.
    """
    eps_c = abs(eps_c)
    return f4 * eps_c ** (-f5) * shift_factor


# ---------------------------------------------------------------------------
# MEPDG / NCHRP 1-37A (2004) bottom-up fatigue cracking model
# ---------------------------------------------------------------------------

def mepdg_fatigue_C(Va_percent, Vbe_percent):
    """
    MEPDG mix-conditioning factor C = 10^M,
    M = 4.84 * (Vbe / (Va + Vbe) - 0.69)

    Parameters
    ----------
    Va_percent : float
        Air voids, percent by volume (typical dense-graded HMA: 4-8%).
    Vbe_percent : float
        Effective asphalt (binder) content, percent by volume (typical: 9-13%).
    """
    M = 4.84 * (Vbe_percent / (Va_percent + Vbe_percent) - 0.69)
    return 10 ** M


def fatigue_life_mepdg(eps_t, E1_psi, Va_percent=7.0, Vbe_percent=11.0, k1=1.0):
    """
    MEPDG / NCHRP 1-37A bottom-up (alligator) fatigue cracking model.

    Nf = 0.00432 * k1 * C * eps_t^-3.9492 * E1^-1.281

    NOTE: Va/Vbe are mix-design inputs, not outputs of the layered elastic
    analysis. The defaults below are typical dense-graded HMA values -
    replace them with your actual mix design before reporting results.
    k1 is the (national or locally calibrated) calibration coefficient;
    1.0 is the uncalibrated national value.

    Parameters
    ----------
    eps_t : float
        Tensile strain magnitude at the bottom of the AC layer (in/in).
    E1_psi : float
        AC layer modulus (psi).
    Va_percent, Vbe_percent : float
        Air voids and effective binder content, percent by volume.
    k1 : float
        Calibration coefficient.

    Returns
    -------
    Nf : float
        Allowable number of load repetitions before fatigue cracking.
    """
    eps_t = abs(eps_t)
    C = mepdg_fatigue_C(Va_percent, Vbe_percent)
    return 0.00432 * k1 * C * eps_t ** (-3.9492) * E1_psi ** (-1.281)


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------

def design_life_summary(eps_t, eps_c, E1_psi, include_mepdg=True, **kwargs):
    """
    Compute Nf (AI), Nd (AI), optionally Nf (MEPDG), and the governing
    (lowest) life among the AI pair.

    kwargs are forwarded to the underlying model functions where the
    parameter name matches (f1..f5, shift_factor, Va_percent, Vbe_percent, k1).
    """
    ai_kwargs = {k: v for k, v in kwargs.items() if k in ('f1', 'f2', 'f3', 'shift_factor')}
    Nf_ai = fatigue_life_ai(eps_t, E1_psi, **ai_kwargs)

    rut_kwargs = {k: v for k, v in kwargs.items() if k in ('f4', 'f5', 'shift_factor')}
    Nd_ai = rutting_life_ai(eps_c, **rut_kwargs)

    result = {
        "Nf_AI": Nf_ai,
        "Nd_AI": Nd_ai,
        "governing_AI": "fatigue" if Nf_ai < Nd_ai else "rutting",
        "design_life_AI": min(Nf_ai, Nd_ai),
    }

    if include_mepdg:
        mepdg_kwargs = {k: v for k, v in kwargs.items() if k in ('Va_percent', 'Vbe_percent', 'k1')}
        result["Nf_MEPDG"] = fatigue_life_mepdg(eps_t, E1_psi, **mepdg_kwargs)

    return result
