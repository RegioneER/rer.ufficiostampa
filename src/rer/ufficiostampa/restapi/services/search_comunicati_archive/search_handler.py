from datetime import datetime
from plone.app.event.base import default_timezone
from urllib.parse import urlencode
from zExceptions import BadRequest

import logging
import lxml.etree
import os
import requests
import zoneinfo


logger = logging.getLogger(__name__)


def to_datetime(data_e_ora):
    if not data_e_ora:
        return None
    dt_naive = datetime.strptime(data_e_ora, "%Y-%m-%d-%H:%M")

    local_tz = zoneinfo.ZoneInfo(default_timezone())
    return dt_naive.replace(tzinfo=local_tz)


class ServiceError(Exception):
    pass


class Service:
    allowed = []
    required = []

    @property
    def base_url(self):
        return os.environ.get("COMUNICATI_OLD_WS_URL", default="")

    @property
    def service_name(self):
        return os.environ.get("COMUNICATI_OLD_SERVICE_NAME", default="")

    @property
    def timeout(self):
        return os.environ.get("COMUNICATI_OLD_TIMEOUT", default=60)

    def parse_response(self, xmlbytes):
        raise NotImplementedError

    def __init__(self, *args, **kw):
        if args:
            raise BadRequest(f"No positional parameters allowed: {args}")

        if not self.service_name or not self.base_url:
            raise BadRequest(
                "Missing config: COMUNICATI_OLD_WS_URL or COMUNICATI_OLD_SERVICE_NAME"
            )

        missing = set(self.required) - set(kw)
        unknown = set(kw) - set(self.allowed)
        if missing:
            raise BadRequest(f"Missing required parameters: {', '.join(missing)}")
        if unknown:
            raise BadRequest(f"Unknown parameters: {', '.join(unknown)}")

        params = [(self.service_name, self.__class__.__name__.lower())]

        for k, v in kw.items():
            if v not in [None, ""]:
                params.append((k, str(v)))

        url = f"{self.base_url}?{urlencode(params, True)}"
        self.parse_response(self.read_url(url))

    def read_url(self, url):
        try:
            headers = {
                "User-Agent": "Plone RER",
            }
            # text
            return requests.get(url, timeout=self.timeout, headers=headers).content
        except Exception:
            logger.exception("Error reading %s (timeout=%s)", url, self.timeout)
            return ""


class XmlService(Service):
    root = None

    def parse_response(self, xmlbytes):
        # raise ServiceError("OOPS!")

        try:
            root = lxml.etree.fromstring(xmlbytes)
            if root.tag == "Error":
                raise ServiceError("Error from XML service: %s" % root.text)
        except lxml.etree.XMLSyntaxError:
            # could be an HTML, possibly with <title>Server Unavailable</title>
            raise ServiceError(
                "Cannot parse XML: %s..."
                % xmlbytes[:100].replace("\n", "").replace("\r", "")
            )
        self.root = root

    def tostring(self):
        return lxml.etree.tostring(self.root)


class BinaryService(Service):
    content = None

    def parse_response(self, stream):
        self.content = stream.read()


class RicercaComunicatiAdvanced(XmlService):
    required = []
    allowed = [
        "codStruttura",  # string 10
        "codArea",  # string 10
        "titolo",  # string 255
        "oggetto",  # string 255
        "testo",  # string 255
        "dataDa",  # string YYYY-MM-DD
        "dataA",  # string YYYY-MM-DD
        "nrMaxComunicati",  # int
        "soloPrincipale",  # int (def. 0)
        "parolechiave",  # string
        "tiporicerca",  # string
        "cercaIn",  # string
    ]

    def __init__(self, *args, **kw):
        kw = kw.copy()
        self.empty_if_errors = kw.pop("empty_if_errors", True)
        super().__init__(*args, **kw)

    def parse_response(self, xmlbytes):
        try:
            super().parse_response(xmlbytes)
        except ServiceError as e:
            logger.error("RicercaComunicatiAdvanced (service.py, line 176) - %s" % e)
            if self.empty_if_errors:
                self.root = None
            else:
                raise

    def as_list(self):
        res_dict = {}
        if self.root is None:
            res_dict["status"] = "timeout"
            res_dict["results"] = []

        else:
            res_dict["status"] = "ok"
            res_dict["results"] = [
                {
                    "codice": elem.attrib["cod"],
                    "struttura": self.get_child_value(elem, "Struttura"),
                    "area": self.get_child_value(elem, "Area"),
                    "titolo": self.get_child_value(elem, "Titolo"),
                    "oggetto": self.get_child_value(elem, "Oggetto"),
                    "permalink": self.get_child_value(elem, "Permalink"),
                    "data_e_ora": to_datetime(self.get_child_value(elem, "DataEOra")),
                }
                for elem in self.root
            ]

        return res_dict

    def get_child_value(self, elem, name):
        node = elem.find(name)
        if node is None:
            return ""
        return node.text


class DettaglioComunicato(XmlService):
    required = ["codComunicato"]
    allowed = [
        "codComunicato",  # int
    ]

    def parse_response(self, xmlbytes):
        try:
            super().parse_response(xmlbytes)
        except ServiceError as e:
            logger.error("DettaglioComunicato (service.py, line 206) - %s" % e)
            self.root = None

    @property
    def comunicato(self):
        root = self.root
        if root is None:
            return
        codice = root.attrib["cod"]

        elenco_allegati = root.find("ElencoAllegati")
        if elenco_allegati is None:
            elenco_allegati = []
        permalink = root.find("Permalink")
        return {
            "codice": codice,
            "struttura": root.find("Struttura").text,
            "area": root.find("Area").text,
            "data_e_ora": to_datetime(root.find("DataEOra").text),
            "permalink": permalink and permalink.text or "",
            "title": root.find("Titolo").text,
            "titolo": root.find("Titolo").text,
            "oggetto": root.find("Oggetto").text,
            "sommario": root.find("Sommario").text,
            "protocollo": root.find("Protocollo").text,
            "testo_completo": root.find("TestoCompleto").text,
            "allegati": list(map(self.extractAllegati, elenco_allegati)),
        }

    def extractAllegati(self, allegato):
        if "cronacabianca" not in self.base_url:
            codice = self.root.attrib["cod"]
            querystring = urlencode(
                [
                    (self.service_name, "DettaglioAllegato"),
                    ("codComunicato", codice),
                    ("nomeFile", allegato.attrib["nome"].encode("utf-8")),
                ]
            )
            return {
                "nome": allegato.attrib["nome"],
                "url": f"{self.base_url}?{querystring}",
            }
        else:
            return {
                "nome": allegato.attrib["nome"],
                "url": allegato.find("Url") is not None
                and allegato.find("Url").text
                or "",
            }


class DettaglioAllegato(BinaryService):
    required = ["codComunicato", "nomeFile"]
    allowed = [
        "codComunicato",  # int
        "nomeFile",  # string
    ]
