"""
Servicio de integración con el SII para emisión de DTEs (boletas electrónicas).

REQUISITOS PREVIOS:
1. Obtener certificado digital de firma electrónica (pfx/p12) de una entidad acreditada
2. Registrar el certificado en el SII en https://misiir.sii.cl
3. Obtener resolución de emisor DTE del SII
4. Configurar las variables SII_* en .env

AMBIENTE:
- certificacion: https://maullin.sii.cl (para pruebas, sin validez legal)
- produccion: https://palena.sii.cl (con validez legal)

Documentación oficial: https://www.sii.cl/factura_electronica/factura_mercado/DTE_Specs.pdf
"""

import os
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.config import settings
from app.models.sale import Sale
from app.models.company import Company


TIPO_BOLETA = "39"

SII_URLS = {
    "certificacion": {
        "auth": "https://maullin.sii.cl/DTEWS/GetTokenFromSeed.jws",
        "upload": "https://maullin.sii.cl/cgi_dte/UPL/DTEUpload",
        "consulta": "https://maullin.sii.cl/DTEWS/QueryEstDte.jws",
    },
    "produccion": {
        "auth": "https://palena.sii.cl/DTEWS/GetTokenFromSeed.jws",
        "upload": "https://palena.sii.cl/cgi_dte/UPL/DTEUpload",
        "consulta": "https://palena.sii.cl/DTEWS/QueryEstDte.jws",
    }
}


def emit_boleta(db: Session, sale: Sale) -> dict:
    """
    Genera y envía una boleta electrónica al SII.
    Retorna el track_id del envío.

    NOTA: Esta integración requiere configuración previa del certificado digital SII.
    Ver instrucciones en la documentación del proyecto.
    """
    if not settings.SII_RUT_EMISOR or not settings.SII_CERT_PATH:
        raise ValueError(
            "Integración SII no configurada. "
            "Configure SII_RUT_EMISOR, SII_CERT_PATH y SII_CERT_PASSWORD en .env"
        )

    company = db.query(Company).first()
    if not company:
        raise ValueError("No hay información de empresa configurada")

    xml_dte = _build_dte_xml(sale, company)
    signed_xml = _sign_xml(xml_dte)
    token = _get_sii_token()
    track_id = _upload_dte(signed_xml, token)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    xml_path = os.path.join(settings.UPLOAD_DIR, f"dte_sale_{sale.id}.xml")
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(signed_xml)

    sale.dte_tipo = TIPO_BOLETA
    sale.dte_fecha_emision = datetime.now()
    sale.dte_track_id = str(track_id)
    sale.dte_xml_path = xml_path
    sale.dte_enviado = True

    db.commit()
    return {"track_id": track_id}


def _build_dte_xml(sale: Sale, company: Company) -> str:
    """Construye el XML del DTE según especificaciones SII."""
    from lxml import etree

    now = datetime.now()
    folio = sale.folio or sale.id

    dte = etree.Element("DTE", version="1.0")
    documento = etree.SubElement(dte, "Documento", ID=f"DTE-{TIPO_BOLETA}-{folio}")

    encabezado = etree.SubElement(documento, "Encabezado")

    id_doc = etree.SubElement(encabezado, "IdDoc")
    etree.SubElement(id_doc, "TipoDTE").text = TIPO_BOLETA
    etree.SubElement(id_doc, "Folio").text = str(folio)
    etree.SubElement(id_doc, "FchEmis").text = now.strftime("%Y-%m-%d")
    etree.SubElement(id_doc, "IndServicio").text = "3"
    etree.SubElement(id_doc, "MntBruto").text = "1"
    etree.SubElement(id_doc, "FmaPago").text = "1"

    emisor = etree.SubElement(encabezado, "Emisor")
    etree.SubElement(emisor, "RUTEmisor").text = company.rut
    etree.SubElement(emisor, "RznSoc").text = company.razon_social
    etree.SubElement(emisor, "GiroEmis").text = company.giro or "Comercio al por menor"
    etree.SubElement(emisor, "DirOrigen").text = company.direccion or ""
    etree.SubElement(emisor, "CmnaOrigen").text = company.comuna or ""

    if company.sii_resolucion_numero:
        etree.SubElement(emisor, "Telefono").text = company.telefono or ""
        etree.SubElement(emisor, "CdgSIISucur").text = "0"

    if sale.customer_rut:
        receptor = etree.SubElement(encabezado, "Receptor")
        etree.SubElement(receptor, "RUTRecep").text = sale.customer_rut
        etree.SubElement(receptor, "RznSocRecep").text = sale.customer_name or "Consumidor Final"

    totales = etree.SubElement(encabezado, "Totales")
    etree.SubElement(totales, "MntNeto").text = str(int(sale.subtotal))
    etree.SubElement(totales, "TasaIVA").text = "19"
    etree.SubElement(totales, "IVA").text = str(int(sale.iva_amount))
    etree.SubElement(totales, "MntTotal").text = str(int(sale.total))

    for i, item in enumerate(sale.items, start=1):
        detalle = etree.SubElement(documento, "Detalle")
        etree.SubElement(detalle, "NroLinDet").text = str(i)
        etree.SubElement(detalle, "NmbItem").text = item.product.name if item.product else f"Producto {item.product_id}"
        etree.SubElement(detalle, "QtyItem").text = str(item.quantity)
        etree.SubElement(detalle, "PrcItem").text = str(int(item.unit_price))
        etree.SubElement(detalle, "MontoItem").text = str(int(item.subtotal))

    if company.sii_resolucion_numero:
        timbre = etree.SubElement(documento, "TED", version="1.0")
        dd = etree.SubElement(timbre, "DD")
        etree.SubElement(dd, "RE").text = company.rut
        etree.SubElement(dd, "TD").text = TIPO_BOLETA
        etree.SubElement(dd, "F").text = str(folio)
        etree.SubElement(dd, "FE").text = now.strftime("%Y-%m-%dT%H:%M:%S")
        etree.SubElement(dd, "RR").text = sale.customer_rut or "66666666-6"
        etree.SubElement(dd, "RSR").text = sale.customer_name or "Consumidor Final"
        etree.SubElement(dd, "MNT").text = str(int(sale.total))
        etree.SubElement(dd, "IT1").text = sale.items[0].product.name if sale.items and sale.items[0].product else "Item"
        etree.SubElement(timbre, "FRMT", algoritmo="SHA1withRSA").text = "PENDIENTE_FIRMA_CAF"

    return etree.tostring(dte, encoding="unicode", pretty_print=True)


def _sign_xml(xml_str: str) -> str:
    """
    Firma el XML con el certificado digital.
    Requiere signxml y el certificado .pfx configurado.
    """
    if not settings.SII_CERT_PATH or not os.path.exists(settings.SII_CERT_PATH):
        return xml_str

    try:
        from lxml import etree
        from signxml import XMLSigner

        with open(settings.SII_CERT_PATH, "rb") as f:
            cert_data = f.read()

        root = etree.fromstring(xml_str.encode())
        signer = XMLSigner()
        signed_root = signer.sign(root, pkcs12_data=cert_data, pkcs12_password=settings.SII_CERT_PASSWORD.encode())
        return etree.tostring(signed_root, encoding="unicode", pretty_print=True)
    except Exception as e:
        raise ValueError(f"Error firmando DTE: {e}")


def _get_sii_token() -> str:
    """Obtiene token de autenticación del SII."""
    try:
        import zeep
        urls = SII_URLS.get(settings.SII_AMBIENTE, SII_URLS["certificacion"])
        client = zeep.Client(urls["auth"])
        seed_response = client.service.getSeed()
        seed = seed_response["RESP_BODY"]["SEMILLA"]

        xml_seed = f"""<getToken><item><Semilla>{seed}</Semilla></item></getToken>"""
        signed_seed = _sign_xml(xml_seed)

        token_response = client.service.getToken(signed_seed)
        return token_response["RESP_BODY"]["TOKEN"]
    except Exception as e:
        raise ValueError(f"Error obteniendo token SII: {e}")


def _upload_dte(signed_xml: str, token: str) -> str:
    """Envía el DTE al SII y retorna el track_id."""
    try:
        import httpx

        urls = SII_URLS.get(settings.SII_AMBIENTE, SII_URLS["certificacion"])
        headers = {"Cookie": f"TOKEN={token}"}
        files = {"archivo": ("dte.xml", signed_xml.encode("utf-8"), "text/xml")}

        response = httpx.post(urls["upload"], headers=headers, files=files, timeout=30)
        response.raise_for_status()

        from lxml import etree
        root = etree.fromstring(response.content)
        track_id = root.findtext(".//TRACKID")
        return track_id or "PENDIENTE"
    except Exception as e:
        raise ValueError(f"Error enviando DTE al SII: {e}")
