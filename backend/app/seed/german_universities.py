# German higher-education catalogue for CampusVoice.
# Sources: HRK university structure list (https://www.hrk.de/hrk-at-a-glance/structure/universities)
# and Hochschulkompass (https://www.hochschulkompass.de), version May 2026.
# Domains verified against official university websites and existing allowlists.

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

STUDENT_PREFIXES = ("stud.", "student.", "students.")

NON_DE_TLD_ALLOWLIST: frozenset[str] = frozenset(
    {
        "iu.org",
        "code.berlin",
        "esmt.berlin",
        "whu.edu",
        "constructor.university",
        "gisma.com",
        "bard-college-berlin.de",
    }
)


class UniType(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    APPLIED_SCIENCES = "applied_sciences"
    ART_MUSIC = "art_music"
    CHURCH = "church"


@dataclass(frozen=True)
class GermanUniversity:
    name: str
    short_name: str | None
    aliases: tuple[str, ...]
    domain: str
    extra_domains: tuple[str, ...]
    city: str
    state: str
    type: UniType
    website: str


def _u(
    name: str,
    *,
    short_name: str | None = None,
    aliases: tuple[str, ...] = (),
    domain: str,
    extra_domains: tuple[str, ...] = (),
    city: str,
    state: str,
    type: UniType,
    website: str | None = None,
) -> GermanUniversity:
    return GermanUniversity(
        name=name,
        short_name=short_name,
        aliases=aliases,
        domain=domain,
        extra_domains=extra_domains,
        city=city,
        state=state,
        type=type,
        website=website or f"https://www.{domain}",
    )


GERMAN_UNIVERSITIES: tuple[GermanUniversity, ...] = (
    # --- Public universities (Universitäten) ---
    _u("Technische Universität München", short_name="TUM", aliases=("TUM", "TU München", "TU Munich", "Technical University of Munich", "Technische Universität München"), domain="tum.de", extra_domains=("mytum.de",), city="München", state="Bayern", type=UniType.PUBLIC),
    _u("Ludwig-Maximilians-Universität München", short_name="LMU", aliases=("LMU", "LMU München", "Ludwig-Maximilians-Universität"), domain="lmu.de", city="München", state="Bayern", type=UniType.PUBLIC),
    _u("Friedrich-Alexander-Universität Erlangen-Nürnberg", short_name="FAU", aliases=("FAU", "FAU Erlangen-Nürnberg", "Universität Erlangen-Nürnberg"), domain="fau.de", extra_domains=("uni-erlangen.de",), city="Erlangen", state="Bayern", type=UniType.PUBLIC),
    _u("Julius-Maximilians-Universität Würzburg", short_name="JMU", aliases=("Uni Würzburg", "Universität Würzburg", "JMU Würzburg"), domain="uni-wuerzburg.de", city="Würzburg", state="Bayern", type=UniType.PUBLIC),
    _u("Universität Regensburg", aliases=("Uni Regensburg", "UR"), domain="uni-regensburg.de", city="Regensburg", state="Bayern", type=UniType.PUBLIC),
    _u("Universität Passau", aliases=("Uni Passau",), domain="uni-passau.de", city="Passau", state="Bayern", type=UniType.PUBLIC),
    _u("Universität Bayreuth", aliases=("Uni Bayreuth",), domain="uni-bayreuth.de", extra_domains=("ubt.de",), city="Bayreuth", state="Bayern", type=UniType.PUBLIC),
    _u("Otto-Friedrich-Universität Bamberg", aliases=("Uni Bamberg", "Universität Bamberg"), domain="uni-bamberg.de", city="Bamberg", state="Bayern", type=UniType.PUBLIC),
    _u("Universität Augsburg", aliases=("Uni Augsburg",), domain="uni-augsburg.de", city="Augsburg", state="Bayern", type=UniType.PUBLIC),
    _u("Universität Hohenheim", aliases=("Uni Hohenheim", "Hohenheim"), domain="uni-hohenheim.de", city="Stuttgart", state="Baden-Württemberg", type=UniType.PUBLIC),
    _u("Universität der Bundeswehr München", short_name="UniBw München", aliases=("UniBw München", "Bundeswehr Universität München"), domain="unibw.de", city="Neubiberg", state="Bayern", type=UniType.PUBLIC),
    _u("Technische Universität Berlin", short_name="TU Berlin", aliases=("TU Berlin", "Technische Universität Berlin"), domain="tu-berlin.de", city="Berlin", state="Berlin", type=UniType.PUBLIC),
    _u("Freie Universität Berlin", short_name="FU Berlin", aliases=("FU Berlin", "Freie Universität", "FU"), domain="fu-berlin.de", city="Berlin", state="Berlin", type=UniType.PUBLIC),
    _u("Humboldt-Universität zu Berlin", short_name="HU Berlin", aliases=("HU Berlin", "Humboldt-Universität", "HU"), domain="hu-berlin.de", city="Berlin", state="Berlin", type=UniType.PUBLIC),
    _u("Charité – Universitätsmedizin Berlin", short_name="Charité", aliases=("Charité", "Charité Berlin"), domain="charite.de", city="Berlin", state="Berlin", type=UniType.PUBLIC),
    _u("Ruprecht-Karls-Universität Heidelberg", short_name="Uni Heidelberg", aliases=("Uni Heidelberg", "Universität Heidelberg", "Heidelberg University"), domain="uni-heidelberg.de", city="Heidelberg", state="Baden-Württemberg", type=UniType.PUBLIC),
    _u("Albert-Ludwigs-Universität Freiburg", short_name="Uni Freiburg", aliases=("Uni Freiburg", "Universität Freiburg", "ALU Freiburg"), domain="uni-freiburg.de", city="Freiburg", state="Baden-Württemberg", type=UniType.PUBLIC),
    _u("Eberhard Karls Universität Tübingen", short_name="Uni Tübingen", aliases=("Uni Tübingen", "Universität Tübingen"), domain="uni-tuebingen.de", city="Tübingen", state="Baden-Württemberg", type=UniType.PUBLIC),
    _u("Universität Konstanz", aliases=("Uni Konstanz",), domain="uni-konstanz.de", city="Konstanz", state="Baden-Württemberg", type=UniType.PUBLIC),
    _u("Universität Ulm", aliases=("Uni Ulm",), domain="uni-ulm.de", city="Ulm", state="Baden-Württemberg", type=UniType.PUBLIC),
    _u("Universität Stuttgart", aliases=("Uni Stuttgart",), domain="uni-stuttgart.de", city="Stuttgart", state="Baden-Württemberg", type=UniType.PUBLIC),
    _u("Universität Mannheim", aliases=("Uni Mannheim",), domain="uni-mannheim.de", city="Mannheim", state="Baden-Württemberg", type=UniType.PUBLIC),
    _u("Karlsruher Institut für Technologie", short_name="KIT", aliases=("KIT", "Karlsruhe Institute of Technology", "Karlsruher Institut für Technologie"), domain="kit.edu", city="Karlsruhe", state="Baden-Württemberg", type=UniType.PUBLIC),
    _u("RWTH Aachen University", short_name="RWTH", aliases=("RWTH", "RWTH Aachen", "RWTH Aachen University", "Rheinisch-Westfälische Technische Hochschule Aachen"), domain="rwth-aachen.de", city="Aachen", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Universität zu Köln", short_name="Uni Köln", aliases=("Uni Köln", "Universität Köln", "UoC"), domain="uni-koeln.de", city="Köln", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Rheinische Friedrich-Wilhelms-Universität Bonn", short_name="Uni Bonn", aliases=("Uni Bonn", "Universität Bonn", "Rheinische Friedrich-Wilhelms-Universität"), domain="uni-bonn.de", city="Bonn", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Heinrich-Heine-Universität Düsseldorf", short_name="HHU", aliases=("HHU", "Uni Düsseldorf", "Heinrich-Heine-Universität"), domain="hhu.de", extra_domains=("uni-duesseldorf.de",), city="Düsseldorf", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Universität Duisburg-Essen", short_name="UDE", aliases=("UDE", "Uni Duisburg-Essen", "Universität Duisburg-Essen"), domain="uni-due.de", extra_domains=("uni-duisburg-essen.de",), city="Duisburg", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Ruhr-Universität Bochum", short_name="RUB", aliases=("RUB", "Ruhr-Universität", "Uni Bochum"), domain="rub.de", extra_domains=("uni-bochum.de",), city="Bochum", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Technische Universität Dortmund", short_name="TU Dortmund", aliases=("TU Dortmund", "Technische Universität Dortmund"), domain="tu-dortmund.de", city="Dortmund", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Westfälische Wilhelms-Universität Münster", short_name="WWU", aliases=("WWU Münster", "Uni Münster", "Universität Münster"), domain="uni-muenster.de", city="Münster", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Universität Bielefeld", aliases=("Uni Bielefeld",), domain="uni-bielefeld.de", city="Bielefeld", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Universität Paderborn", aliases=("Uni Paderborn",), domain="uni-paderborn.de", city="Paderborn", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Universität Siegen", aliases=("Uni Siegen",), domain="uni-siegen.de", city="Siegen", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Bergische Universität Wuppertal", aliases=("Uni Wuppertal", "BUW"), domain="uni-wuppertal.de", city="Wuppertal", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("FernUniversität in Hagen", aliases=("FernUni Hagen", "Fernuniversität Hagen"), domain="fernuni-hagen.de", city="Hagen", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Goethe-Universität Frankfurt am Main", short_name="Goethe Uni", aliases=("Goethe-Universität", "Uni Frankfurt", "Goethe Uni Frankfurt"), domain="uni-frankfurt.de", city="Frankfurt am Main", state="Hessen", type=UniType.PUBLIC),
    _u("Philipps-Universität Marburg", aliases=("Uni Marburg", "Universität Marburg"), domain="uni-marburg.de", city="Marburg", state="Hessen", type=UniType.PUBLIC),
    _u("Justus-Liebig-Universität Gießen", aliases=("Uni Gießen", "JLU Gießen"), domain="uni-giessen.de", city="Gießen", state="Hessen", type=UniType.PUBLIC),
    _u("Universität Kassel", aliases=("Uni Kassel",), domain="uni-kassel.de", city="Kassel", state="Hessen", type=UniType.PUBLIC),
    _u("Technische Universität Darmstadt", short_name="TU Darmstadt", aliases=("TU Darmstadt", "Technische Universität Darmstadt"), domain="tu-darmstadt.de", city="Darmstadt", state="Hessen", type=UniType.PUBLIC),
    _u("Johannes Gutenberg-Universität Mainz", short_name="JGU", aliases=("JGU", "Uni Mainz", "Universität Mainz"), domain="uni-mainz.de", city="Mainz", state="Rheinland-Pfalz", type=UniType.PUBLIC),
    _u("Universität Trier", aliases=("Uni Trier",), domain="uni-trier.de", city="Trier", state="Rheinland-Pfalz", type=UniType.PUBLIC),
    _u("Rheinland-Pfälzische Technische Universität Kaiserslautern-Landau", short_name="RPTU", aliases=("RPTU", "TU Kaiserslautern", "Universität Kaiserslautern"), domain="rptu.de", extra_domains=("uni-kl.de",), city="Kaiserslautern", state="Rheinland-Pfalz", type=UniType.PUBLIC),
    _u("Universität Koblenz", aliases=("Uni Koblenz",), domain="uni-koblenz.de", city="Koblenz", state="Rheinland-Pfalz", type=UniType.PUBLIC),
    _u("Universität des Saarlandes", aliases=("Uni Saarland", "UdS"), domain="uni-saarland.de", city="Saarbrücken", state="Saarland", type=UniType.PUBLIC),
    _u("Universität Hamburg", aliases=("Uni Hamburg", "UHH"), domain="uni-hamburg.de", city="Hamburg", state="Hamburg", type=UniType.PUBLIC),
    _u("Technische Universität Hamburg", short_name="TUHH", aliases=("TUHH", "TU Hamburg", "Technische Universität Hamburg"), domain="tuhh.de", city="Hamburg", state="Hamburg", type=UniType.PUBLIC),
    _u("HafenCity Universität Hamburg", short_name="HCU", aliases=("HCU", "HafenCity Universität"), domain="hcu-hamburg.de", city="Hamburg", state="Hamburg", type=UniType.PUBLIC),
    _u("Helmut-Schmidt-Universität der Bundeswehr Hamburg", short_name="HSU", aliases=("HSU", "Helmut-Schmidt-Universität", "Universität der Bundeswehr Hamburg"), domain="hsu-hh.de", city="Hamburg", state="Hamburg", type=UniType.PUBLIC),
    _u("Universität Bremen", aliases=("Uni Bremen",), domain="uni-bremen.de", city="Bremen", state="Bremen", type=UniType.PUBLIC),
    _u("Leibniz Universität Hannover", aliases=("Uni Hannover", "LUH", "Leibniz Universität"), domain="uni-hannover.de", city="Hannover", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Technische Universität Braunschweig", short_name="TU Braunschweig", aliases=("TU Braunschweig", "Technische Universität Braunschweig"), domain="tu-braunschweig.de", city="Braunschweig", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Technische Universität Clausthal", short_name="TU Clausthal", aliases=("TU Clausthal", "Technische Universität Clausthal"), domain="tu-clausthal.de", city="Clausthal-Zellerfeld", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Georg-August-Universität Göttingen", aliases=("Uni Göttingen", "Universität Göttingen"), domain="uni-goettingen.de", city="Göttingen", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Carl von Ossietzky Universität Oldenburg", aliases=("Uni Oldenburg", "Universität Oldenburg"), domain="uol.de", extra_domains=("uni-oldenburg.de",), city="Oldenburg", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Universität Osnabrück", aliases=("Uni Osnabrück",), domain="uos.de", extra_domains=("uni-osnabrueck.de",), city="Osnabrück", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Universität Hildesheim", aliases=("Uni Hildesheim",), domain="uni-hildesheim.de", city="Hildesheim", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Leuphana Universität Lüneburg", aliases=("Leuphana", "Uni Lüneburg"), domain="leuphana.de", city="Lüneburg", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Universität Vechta", aliases=("Uni Vechta",), domain="uni-vechta.de", city="Vechta", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Medizinische Hochschule Hannover", short_name="MHH", aliases=("MHH", "Medizinische Hochschule Hannover"), domain="mh-hannover.de", city="Hannover", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Tierärztliche Hochschule Hannover", short_name="TiHo", aliases=("TiHo", "Tierärztliche Hochschule Hannover"), domain="tiho-hannover.de", city="Hannover", state="Niedersachsen", type=UniType.PUBLIC),
    _u("Christian-Albrechts-Universität zu Kiel", short_name="CAU", aliases=("CAU Kiel", "Uni Kiel", "Universität Kiel"), domain="uni-kiel.de", city="Kiel", state="Schleswig-Holstein", type=UniType.PUBLIC),
    _u("Universität zu Lübeck", aliases=("Uni Lübeck",), domain="uni-luebeck.de", city="Lübeck", state="Schleswig-Holstein", type=UniType.PUBLIC),
    _u("Europa-Universität Flensburg", aliases=("EUF", "Uni Flensburg"), domain="uni-flensburg.de", city="Flensburg", state="Schleswig-Holstein", type=UniType.PUBLIC),
    _u("Universität Potsdam", aliases=("Uni Potsdam",), domain="uni-potsdam.de", city="Potsdam", state="Brandenburg", type=UniType.PUBLIC),
    _u("European University Viadrina Frankfurt (Oder)", short_name="Viadrina", aliases=("Viadrina", "Europa-Universität Viadrina", "European University Viadrina"), domain="europa-uni.de", city="Frankfurt (Oder)", state="Brandenburg", type=UniType.PUBLIC),
    _u("Brandenburgische Technische Universität Cottbus-Senftenberg", short_name="BTU", aliases=("BTU", "BTU Cottbus-Senftenberg"), domain="b-tu.de", city="Cottbus", state="Brandenburg", type=UniType.PUBLIC),
    _u("Technische Universität Dresden", short_name="TU Dresden", aliases=("TU Dresden", "Technische Universität Dresden"), domain="tu-dresden.de", city="Dresden", state="Sachsen", type=UniType.PUBLIC),
    _u("Universität Leipzig", aliases=("Uni Leipzig",), domain="uni-leipzig.de", city="Leipzig", state="Sachsen", type=UniType.PUBLIC),
    _u("Technische Universität Chemnitz", short_name="TU Chemnitz", aliases=("TU Chemnitz", "Technische Universität Chemnitz"), domain="tu-chemnitz.de", city="Chemnitz", state="Sachsen", type=UniType.PUBLIC),
    _u("Technische Universität Bergakademie Freiberg", short_name="TU Freiberg", aliases=("TU Freiberg", "TU Bergakademie Freiberg"), domain="tu-freiberg.de", city="Freiberg", state="Sachsen", type=UniType.PUBLIC),
    _u("Martin-Luther-Universität Halle-Wittenberg", aliases=("MLU", "Uni Halle", "Universität Halle-Wittenberg"), domain="uni-halle.de", city="Halle (Saale)", state="Sachsen-Anhalt", type=UniType.PUBLIC),
    _u("Otto-von-Guericke-Universität Magdeburg", short_name="OvGU", aliases=("OvGU", "Uni Magdeburg", "Universität Magdeburg"), domain="ovgu.de", city="Magdeburg", state="Sachsen-Anhalt", type=UniType.PUBLIC),
    _u("Friedrich-Schiller-Universität Jena", aliases=("Uni Jena", "FSU Jena"), domain="uni-jena.de", city="Jena", state="Thüringen", type=UniType.PUBLIC),
    _u("Bauhaus-Universität Weimar", aliases=("Bauhaus-Universität", "Uni Weimar"), domain="uni-weimar.de", city="Weimar", state="Thüringen", type=UniType.PUBLIC),
    _u("Technische Universität Ilmenau", short_name="TU Ilmenau", aliases=("TU Ilmenau", "Technische Universität Ilmenau"), domain="tu-ilmenau.de", city="Ilmenau", state="Thüringen", type=UniType.PUBLIC),
    _u("Universität Erfurt", aliases=("Uni Erfurt",), domain="uni-erfurt.de", city="Erfurt", state="Thüringen", type=UniType.PUBLIC),
    _u("Universität Rostock", aliases=("Uni Rostock",), domain="uni-rostock.de", city="Rostock", state="Mecklenburg-Vorpommern", type=UniType.PUBLIC),
    _u("Universität Greifswald", aliases=("Uni Greifswald",), domain="uni-greifswald.de", city="Greifswald", state="Mecklenburg-Vorpommern", type=UniType.PUBLIC),
    _u("Deutsche Sporthochschule Köln", short_name="DSHS", aliases=("DSHS", "Deutsche Sporthochschule", "Sporthochschule Köln"), domain="dshs-koeln.de", city="Köln", state="Nordrhein-Westfalen", type=UniType.PUBLIC),
    _u("Filmuniversität Babelsberg KONRAD WOLF", aliases=("Filmuni Babelsberg", "Filmuniversität Potsdam"), domain="filmuniversitaet.de", city="Potsdam", state="Brandenburg", type=UniType.PUBLIC),
    # --- Universities of applied sciences (HAW / FH / TH) ---
    _u("Hochschule München", short_name="HM", aliases=("HM", "Hochschule München"), domain="hm.edu", city="München", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Augsburg", aliases=("HS Augsburg",), domain="hs-augsburg.de", city="Augsburg", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Ingolstadt", short_name="THI", aliases=("THI", "Technische Hochschule Ingolstadt"), domain="thi.de", city="Ingolstadt", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Nürnberg Georg Simon Ohm", short_name="TH Nürnberg", aliases=("TH Nürnberg", "Georg Simon Ohm TH"), domain="th-nuernberg.de", city="Nürnberg", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Ostbayerische Technische Hochschule Regensburg", short_name="OTH Regensburg", aliases=("OTH Regensburg", "OTH"), domain="oth-regensburg.de", city="Regensburg", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule für angewandte Wissenschaften Würzburg-Schweinfurt", short_name="FHWS", aliases=("FHWS",), domain="fhws.de", city="Würzburg", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Deggendorf", short_name="THD", aliases=("THD", "TH Deggendorf"), domain="th-deg.de", city="Deggendorf", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Rosenheim", aliases=("TH Rosenheim",), domain="th-rosenheim.de", city="Rosenheim", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Coburg", aliases=("HS Coburg",), domain="hs-coburg.de", city="Coburg", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Landshut", aliases=("HS Landshut",), domain="hs-landshut.de", city="Landshut", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Kempten", aliases=("HS Kempten",), domain="hs-kempten.de", city="Kempten", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Ansbach", aliases=("HS Ansbach",), domain="hs-ansbach.de", city="Ansbach", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Weihenstephan-Triesdorf", aliases=("HSWT", "Weihenstephan-Triesdorf"), domain="hs-weihenstephan.de", city="Freising", state="Bayern", type=UniType.APPLIED_SCIENCES),
    _u("HTW Berlin – Hochschule für Technik und Wirtschaft", short_name="HTW Berlin", aliases=("HTW Berlin", "Hochschule für Technik und Wirtschaft Berlin"), domain="htw-berlin.de", city="Berlin", state="Berlin", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule für Wirtschaft und Recht Berlin", short_name="HWR Berlin", aliases=("HWR Berlin",), domain="hwr-berlin.de", city="Berlin", state="Berlin", type=UniType.APPLIED_SCIENCES),
    _u("Berliner Hochschule für Technik", short_name="BHT", aliases=("BHT", "Beuth Hochschule", "Berliner Hochschule für Technik"), domain="bht-berlin.de", extra_domains=("beuth-hochschule.de",), city="Berlin", state="Berlin", type=UniType.APPLIED_SCIENCES),
    _u("Alice Salomon Hochschule Berlin", short_name="ASH Berlin", aliases=("ASH Berlin", "Alice Salomon Hochschule"), domain="ash-berlin.eu", city="Berlin", state="Berlin", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule für Technik und Wirtschaft des Saarlandes", short_name="htw saar", aliases=("htw saar", "HTW Saar"), domain="htwsaar.de", city="Saarbrücken", state="Saarland", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Karlsruhe", aliases=("HS Karlsruhe",), domain="h-ka.de", city="Karlsruhe", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Mannheim", aliases=("HS Mannheim",), domain="hs-mannheim.de", city="Mannheim", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Pforzheim", aliases=("HS Pforzheim",), domain="hs-pforzheim.de", city="Pforzheim", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Esslingen", aliases=("HS Esslingen",), domain="hs-esslingen.de", city="Esslingen", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Heilbronn", aliases=("HS Heilbronn",), domain="hs-heilbronn.de", city="Heilbronn", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Aalen", aliases=("HS Aalen",), domain="hs-aalen.de", city="Aalen", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Reutlingen", aliases=("HS Reutlingen",), domain="reutlingen-university.de", city="Reutlingen", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Konstanz (HTWG)", short_name="HTWG", aliases=("HTWG Konstanz", "HTWG"), domain="htwg-konstanz.de", city="Konstanz", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Furtwangen", aliases=("HFU", "HS Furtwangen"), domain="hs-furtwangen.de", city="Furtwangen", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Offenburg", aliases=("HS Offenburg",), domain="hs-offenburg.de", city="Offenburg", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule der Medien Stuttgart", short_name="HDM", aliases=("HDM", "Hochschule der Medien"), domain="hdm-stuttgart.de", city="Stuttgart", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Duale Hochschule Baden-Württemberg", short_name="DHBW", aliases=("DHBW", "Duale Hochschule BW"), domain="dhbw.de", city="Stuttgart", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Köln", short_name="TH Köln", aliases=("TH Köln", "Technische Hochschule Köln", "Köln University of Applied Sciences"), domain="th-koeln.de", city="Köln", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Bonn-Rhein-Sieg", short_name="H-BRS", aliases=("H-BRS", "Hochschule Bonn-Rhein-Sieg"), domain="h-brs.de", city="Sankt Augustin", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Düsseldorf", aliases=("HSD", "HS Düsseldorf"), domain="hs-duesseldorf.de", city="Düsseldorf", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Bochum", aliases=("HS Bochum",), domain="hs-bochum.de", city="Bochum", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Fachhochschule Dortmund", short_name="FH Dortmund", aliases=("FH Dortmund",), domain="fh-dortmund.de", city="Dortmund", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Fachhochschule Münster", short_name="FH Münster", aliases=("FH Münster",), domain="fh-muenster.de", city="Münster", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Fachhochschule Bielefeld", short_name="FH Bielefeld", aliases=("FH Bielefeld",), domain="fh-bielefeld.de", city="Bielefeld", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Fachhochschule Aachen", short_name="FH Aachen", aliases=("FH Aachen",), domain="fh-aachen.de", city="Aachen", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Niederrhein", aliases=("HS Niederrhein",), domain="hs-niederrhein.de", city="Krefeld", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Ruhr West", aliases=("HRW", "Hochschule Ruhr West"), domain="hs-ruhrwest.de", city="Mülheim an der Ruhr", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Rhein-Waal", short_name="HSRW", aliases=("HSRW", "Hochschule Rhein-Waal"), domain="hsrw.eu", city="Kleve", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Ostwestfalen-Lippe", short_name="TH OWL", aliases=("TH OWL", "Technische Hochschule OWL"), domain="th-owl.de", city="Lemgo", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Fachhochschule Südwestfalen", short_name="FH SWF", aliases=("FH Südwestfalen", "FH SWF"), domain="fh-swf.de", city="Iserlohn", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Hamm-Lippstadt", aliases=("HSHL",), domain="hs-hamm-lippstadt.de", city="Hamm", state="Nordrhein-Westfalen", type=UniType.APPLIED_SCIENCES),
    _u("Frankfurt University of Applied Sciences", aliases=("Frankfurt UAS", "Frankfurt University of Applied Sciences"), domain="frankfurt-university.de", city="Frankfurt am Main", state="Hessen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Darmstadt", short_name="h_da", aliases=("h_da", "Hochschule Darmstadt"), domain="h-da.de", city="Darmstadt", state="Hessen", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Mittelhessen", short_name="THM", aliases=("THM", "Technische Hochschule Mittelhessen"), domain="thm.de", city="Gießen", state="Hessen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Fulda", aliases=("HS Fulda",), domain="hs-fulda.de", city="Fulda", state="Hessen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule RheinMain", aliases=("HS RheinMain",), domain="hs-rm.de", city="Wiesbaden", state="Hessen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Geisenheim", aliases=("Hochschule Geisenheim University",), domain="hs-geisenheim.de", city="Geisenheim", state="Hessen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Mainz", aliases=("HS Mainz",), domain="hs-mainz.de", city="Mainz", state="Rheinland-Pfalz", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Trier", aliases=("HS Trier",), domain="hochschule-trier.de", city="Trier", state="Rheinland-Pfalz", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Kaiserslautern", aliases=("HS Kaiserslautern",), domain="hs-kl.de", city="Kaiserslautern", state="Rheinland-Pfalz", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Koblenz", aliases=("HS Koblenz",), domain="hs-koblenz.de", city="Koblenz", state="Rheinland-Pfalz", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Worms", aliases=("HS Worms",), domain="hs-worms.de", city="Worms", state="Rheinland-Pfalz", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Ludwigshafen", aliases=("HS Ludwigshafen",), domain="hs-lu.de", city="Ludwigshafen", state="Rheinland-Pfalz", type=UniType.APPLIED_SCIENCES),
    _u("HAW Hamburg", aliases=("HAW Hamburg", "Hochschule für Angewandte Wissenschaften Hamburg"), domain="haw-hamburg.de", city="Hamburg", state="Hamburg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Bremen", aliases=("HS Bremen",), domain="hs-bremen.de", city="Bremen", state="Bremen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Bremerhaven", aliases=("HS Bremerhaven",), domain="hs-bremerhaven.de", city="Bremerhaven", state="Bremen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Hannover", aliases=("HS Hannover",), domain="hs-hannover.de", city="Hannover", state="Niedersachsen", type=UniType.APPLIED_SCIENCES),
    _u("Ostfalia Hochschule für angewandte Wissenschaften", short_name="Ostfalia", aliases=("Ostfalia", "Ostfalia Hochschule"), domain="ostfalia.de", city="Wolfenbüttel", state="Niedersachsen", type=UniType.APPLIED_SCIENCES),
    _u("HAWK Hochschule für angewandte Wissenschaft und Kunst", short_name="HAWK", aliases=("HAWK",), domain="hawk.de", city="Hildesheim", state="Niedersachsen", type=UniType.APPLIED_SCIENCES),
    _u("Jade Hochschule", aliases=("Jade HS",), domain="jade-hs.de", city="Wilhelmshaven", state="Niedersachsen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Osnabrück", aliases=("HS Osnabrück",), domain="hs-osnabrueck.de", city="Osnabrück", state="Niedersachsen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Emden/Leer", aliases=("HS Emden/Leer",), domain="hs-emden-leer.de", city="Emden", state="Niedersachsen", type=UniType.APPLIED_SCIENCES),
    _u("Fachhochschule Kiel", short_name="FH Kiel", aliases=("FH Kiel",), domain="fh-kiel.de", city="Kiel", state="Schleswig-Holstein", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Lübeck", aliases=("TH Lübeck",), domain="th-luebeck.de", city="Lübeck", state="Schleswig-Holstein", type=UniType.APPLIED_SCIENCES),
    _u("Fachhochschule Westküste", aliases=("FH Westküste",), domain="fh-westkueste.de", city="Heide", state="Schleswig-Holstein", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Flensburg", aliases=("HS Flensburg",), domain="hs-flensburg.de", city="Flensburg", state="Schleswig-Holstein", type=UniType.APPLIED_SCIENCES),
    _u("Fachhochschule Potsdam", short_name="FH Potsdam", aliases=("FH Potsdam",), domain="fh-potsdam.de", city="Potsdam", state="Brandenburg", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Wildau", short_name="TH Wildau", aliases=("TH Wildau",), domain="th-wildau.de", city="Wildau", state="Brandenburg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule für nachhaltige Entwicklung Eberswalde", short_name="HNEE", aliases=("HNEE", "Hochschule Eberswalde"), domain="hnee.de", city="Eberswalde", state="Brandenburg", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Wismar", aliases=("HS Wismar",), domain="hs-wismar.de", city="Wismar", state="Mecklenburg-Vorpommern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Stralsund", aliases=("HS Stralsund",), domain="hs-stralsund.de", city="Stralsund", state="Mecklenburg-Vorpommern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Neubrandenburg", aliases=("HS Neubrandenburg",), domain="hs-nb.de", city="Neubrandenburg", state="Mecklenburg-Vorpommern", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Mittweida", aliases=("HS Mittweida",), domain="hs-mittweida.de", city="Mittweida", state="Sachsen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Zittau/Görlitz", short_name="HSZG", aliases=("HSZG", "Hochschule Zittau/Görlitz"), domain="hszg.de", city="Zittau", state="Sachsen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule für Technik und Wirtschaft Dresden", short_name="HTW Dresden", aliases=("HTW Dresden",), domain="htw-dresden.de", city="Dresden", state="Sachsen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule für Technik, Wirtschaft und Kultur Leipzig", short_name="HTWK Leipzig", aliases=("HTWK Leipzig",), domain="htwk-leipzig.de", city="Leipzig", state="Sachsen", type=UniType.APPLIED_SCIENCES),
    _u("Ernst-Abbe-Hochschule Jena", aliases=("EAH Jena",), domain="eah-jena.de", city="Jena", state="Thüringen", type=UniType.APPLIED_SCIENCES),
    _u("Fachhochschule Erfurt", short_name="FH Erfurt", aliases=("FH Erfurt",), domain="fh-erfurt.de", city="Erfurt", state="Thüringen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Nordhausen", aliases=("HS Nordhausen",), domain="hs-nordhausen.de", city="Nordhausen", state="Thüringen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Schmalkalden", aliases=("HS Schmalkalden",), domain="hs-sm.de", city="Schmalkalden", state="Thüringen", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Merseburg", aliases=("HS Merseburg",), domain="hs-merseburg.de", city="Merseburg", state="Sachsen-Anhalt", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Magdeburg-Stendal", aliases=("HS Magdeburg-Stendal",), domain="hs-magdeburg.de", extra_domains=("h2.de",), city="Magdeburg", state="Sachsen-Anhalt", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Anhalt", aliases=("HS Anhalt",), domain="hs-anhalt.de", city="Köthen", state="Sachsen-Anhalt", type=UniType.APPLIED_SCIENCES),
    _u("Hochschule Harz", aliases=("HS Harz",), domain="hs-harz.de", city="Wernigerode", state="Sachsen-Anhalt", type=UniType.APPLIED_SCIENCES),
    _u("Technische Hochschule Ulm", aliases=("TH Ulm",), domain="thu.de", city="Ulm", state="Baden-Württemberg", type=UniType.APPLIED_SCIENCES),
    # --- Private universities ---
    _u("Berlin School of Business and Innovation", short_name="BSBI", aliases=("BSBI", "Berlin School of Business and Innovation"), domain="bsbi.de", city="Berlin", state="Berlin", type=UniType.PRIVATE, website="https://www.bsbi.de"),
    _u("IU International University of Applied Sciences", short_name="IU", aliases=("IU", "IU Internationale Hochschule", "IUBH"), domain="iu.org", extra_domains=("iu.de", "iubh.de"), city="Erfurt", state="Thüringen", type=UniType.PRIVATE, website="https://www.iu.org"),
    _u("GISMA University of Applied Sciences", short_name="GISMA", aliases=("GISMA", "GISMA Business School"), domain="gisma.com", city="Hannover", state="Niedersachsen", type=UniType.PRIVATE, website="https://www.gisma.com"),
    _u("CODE University of Applied Sciences", short_name="CODE", aliases=("CODE", "CODE University"), domain="code.berlin", city="Berlin", state="Berlin", type=UniType.PRIVATE, website="https://code.berlin"),
    _u("Hertie School", aliases=("Hertie School of Governance",), domain="hertie-school.org", city="Berlin", state="Berlin", type=UniType.PRIVATE),
    _u("ESMT Berlin", short_name="ESMT", aliases=("ESMT", "European School of Management and Technology"), domain="esmt.berlin", extra_domains=("esmt.org",), city="Berlin", state="Berlin", type=UniType.PRIVATE, website="https://esmt.berlin"),
    _u("WHU – Otto Beisheim School of Management", short_name="WHU", aliases=("WHU", "WHU Vallendar", "WHU Düsseldorf"), domain="whu.edu", city="Vallendar", state="Rheinland-Pfalz", type=UniType.PRIVATE, website="https://www.whu.edu"),
    _u("Frankfurt School of Finance & Management", aliases=("Frankfurt School",), domain="frankfurt-school.de", city="Frankfurt am Main", state="Hessen", type=UniType.PRIVATE),
    _u("Zeppelin Universität", aliases=("Zeppelin University", "ZU"), domain="zeppelin-university.de", city="Friedrichshafen", state="Baden-Württemberg", type=UniType.PRIVATE),
    _u("Bard College Berlin", aliases=("Bard Berlin", "Bard College Berlin"), domain="bard-college-berlin.de", city="Berlin", state="Berlin", type=UniType.PRIVATE),
    _u("Constructor University", aliases=("Constructor University Bremen", "Jacobs University"), domain="constructor.university", extra_domains=("jacobs-university.de",), city="Bremen", state="Bremen", type=UniType.PRIVATE, website="https://constructor.university"),
    _u("Hochschule Fresenius", aliases=("Fresenius Hochschule",), domain="hs-fresenius.de", city="Idstein", state="Hessen", type=UniType.PRIVATE),
    _u("FOM Hochschule für Oekonomie & Management", short_name="FOM", aliases=("FOM", "FOM Hochschule"), domain="fom.de", city="Essen", state="Nordrhein-Westfalen", type=UniType.PRIVATE),
    _u("Hochschule Macromedia", aliases=("Macromedia", "Macromedia University"), domain="macromedia.de", extra_domains=("macromedia-fachhochschule.de",), city="München", state="Bayern", type=UniType.PRIVATE),
    _u("HMKW Hochschule für Medien, Kommunikation und Wirtschaft", short_name="HMKW", aliases=("HMKW",), domain="hmkw.de", city="Berlin", state="Berlin", type=UniType.PRIVATE),
    _u("EBS Universität für Wirtschaft und Recht", short_name="EBS", aliases=("EBS", "EBS Universität"), domain="ebs.edu", city="Oestrich-Winkel", state="Hessen", type=UniType.PRIVATE, website="https://www.ebs.edu"),
    _u("EBC Hochschule", short_name="EBC", aliases=("EBC", "EBC Hochschule"), domain="ebc-hochschule.de", city="Hamburg", state="Hamburg", type=UniType.PRIVATE),
    _u("Touro University Berlin", aliases=("Touro Berlin",), domain="touroberlin.com", city="Berlin", state="Berlin", type=UniType.PRIVATE, website="https://www.touroberlin.com"),
    _u("Steinbeis-Hochschule", aliases=("Steinbeis University", "Steinbeis-Hochschule Berlin"), domain="steinbeis-hochschule.de", city="Berlin", state="Berlin", type=UniType.PRIVATE),
    _u("Karlshochschule International University", aliases=("Karlshochschule", "Karls"), domain="karlshochschule.de", city="Karlsruhe", state="Baden-Württemberg", type=UniType.PRIVATE),
    _u("Munich Business School", short_name="MBS", aliases=("MBS", "Munich Business School"), domain="munich-business-school.de", city="München", state="Bayern", type=UniType.PRIVATE),
    _u("accadis Hochschule Bad Homburg", short_name="accadis", aliases=("accadis", "accadis Hochschule"), domain="accadis.com", city="Bad Homburg", state="Hessen", type=UniType.PRIVATE, website="https://www.accadis.com"),
    _u("ISM International School of Management", short_name="ISM", aliases=("ISM", "International School of Management"), domain="ism.de", city="Dortmund", state="Nordrhein-Westfalen", type=UniType.PRIVATE),
    _u("Cologne Business School", short_name="CBS", aliases=("CBS", "Cologne Business School"), domain="cbs.de", city="Köln", state="Nordrhein-Westfalen", type=UniType.PRIVATE, website="https://www.cbs.de"),
    _u("SRH University", aliases=("SRH", "SRH Hochschule"), domain="srh-university.de", extra_domains=("srh.de",), city="Heidelberg", state="Baden-Württemberg", type=UniType.PRIVATE),
    _u("SRH Hochschule Berlin", aliases=("SRH Berlin",), domain="srh-hochschule-berlin.de", city="Berlin", state="Berlin", type=UniType.PRIVATE),
    _u("SRH Hochschule Heidelberg", aliases=("SRH Heidelberg",), domain="srh-hochschule-heidelberg.de", city="Heidelberg", state="Baden-Württemberg", type=UniType.PRIVATE),
    _u("SRH Fernhochschule – The Mobile University", aliases=("SRH Fernhochschule",), domain="srh-fernhochschule.de", city="Riedlingen", state="Baden-Württemberg", type=UniType.PRIVATE),
    _u("Universität Witten/Herdecke", aliases=("Uni Witten/Herdecke", "UWH"), domain="uni-wh.de", extra_domains=("uni-witten.de",), city="Witten", state="Nordrhein-Westfalen", type=UniType.PRIVATE),
    # --- Art, music, and design universities ---
    _u("Universität der Künste Berlin", short_name="UdK Berlin", aliases=("UdK", "UdK Berlin", "Universität der Künste"), domain="udk-berlin.de", city="Berlin", state="Berlin", type=UniType.ART_MUSIC),
    _u("Hochschule für bildende Künste Hamburg", short_name="HFBK", aliases=("HFBK", "HFBK Hamburg"), domain="hfbk-hamburg.de", city="Hamburg", state="Hamburg", type=UniType.ART_MUSIC, website="https://www.hfbk-hamburg.de"),
    _u("Folkwang Universität der Künste", aliases=("Folkwang", "Folkwang Uni"), domain="folkwang-uni.de", city="Essen", state="Nordrhein-Westfalen", type=UniType.ART_MUSIC),
    _u("Hochschule für Musik Hanns Eisler Berlin", aliases=("HfM Hanns Eisler", "Hanns Eisler"), domain="hfm-berlin.de", city="Berlin", state="Berlin", type=UniType.ART_MUSIC),
    _u("Hochschule für Musik und Theater München", short_name="HMTM", aliases=("HMTM", "Musikhochschule München", "Hochschule für Musik und Theater München"), domain="musikhochschule-muenchen.de", city="München", state="Bayern", type=UniType.ART_MUSIC, website="https://www.musikhochschule-muenchen.de"),
    _u("Kunsthochschule Berlin-Weißensee", aliases=("KHB", "Weißensee Kunsthochschule"), domain="khb-berlin.de", city="Berlin", state="Berlin", type=UniType.ART_MUSIC, website="https://www.khb-berlin.de"),
    _u("Hochschule für Schauspielkunst Ernst Busch", aliases=("Ernst Busch", "HfS Berlin"), domain="hfs-berlin.de", city="Berlin", state="Berlin", type=UniType.ART_MUSIC),
    _u("Hochschule für Künste Bremen", aliases=("HFK Bremen",), domain="hfk-bremen.de", city="Bremen", state="Bremen", type=UniType.ART_MUSIC),
    # --- Church-affiliated universities ---
    _u("Katholische Universität Eichstätt-Ingolstadt", aliases=("KU Eichstätt", "Katholische Universität"), domain="ku.de", city="Eichstätt", state="Bayern", type=UniType.CHURCH),
)


def all_catalogue_domains() -> set[str]:
    """All primary and extra domains plus common student-mail subdomain prefixes."""
    domains: set[str] = set()
    for uni in GERMAN_UNIVERSITIES:
        for base in (uni.domain, *uni.extra_domains):
            base = base.lower().strip()
            if not base:
                continue
            domains.add(base)
            for prefix in STUDENT_PREFIXES:
                domains.add(f"{prefix}{base}")
    return domains


def domain_to_university() -> dict[str, GermanUniversity]:
    """Map each catalogue domain (primary and extra) to its university record."""
    mapping: dict[str, GermanUniversity] = {}
    for uni in GERMAN_UNIVERSITIES:
        mapping[uni.domain.lower()] = uni
        for extra in uni.extra_domains:
            mapping[extra.lower()] = uni
    return mapping


def seed_rows() -> list[dict[str, object]]:
    """Rows for idempotent DB upsert into the universities table."""
    return [
        {
            "name": uni.name,
            "domain": uni.domain.lower(),
            "city": uni.city,
            "short_name": uni.short_name,
            "aliases": list(uni.aliases),
            "state": uni.state,
            "type": uni.type.value,
            "website": uni.website,
        }
        for uni in GERMAN_UNIVERSITIES
    ]

